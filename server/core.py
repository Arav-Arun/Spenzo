"""Shared plumbing: settings, the current user, dates and HTTP."""
import calendar
import os
import re
from contextvars import ContextVar
from datetime import date, datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

IST = timezone(timedelta(hours=5, minutes=30))

http = httpx.Client(timeout=10.0, headers={"User-Agent": "Mozilla/5.0 (Spenzo)"})


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def now() -> datetime:
    return datetime.now(IST)


def today() -> str:
    """Today's date in India, where Spenzo's users are (the server runs in UTC)."""
    return now().date().isoformat()


def month_range(day: str | None = None) -> tuple[str, str]:
    """First and last day of the month containing `day` (default today)."""
    d = date.fromisoformat(day or today())
    return d.replace(day=1).isoformat(), d.replace(day=calendar.monthrange(d.year, d.month)[1]).isoformat()


def check_date(day: str, *, future_days: int = 1, past_days: int = 400) -> str:
    """Reject dates far from today. Models don't know today's date and tend to guess a year
    from their training; saying today's date in the error lets them retry."""
    try:
        d = date.fromisoformat(day)
    except ValueError:
        raise ValueError(f"'{day}' isn't a date. Use YYYY-MM-DD; today is {today()}.")
    t = date.fromisoformat(today())
    if d > t + timedelta(days=future_days) or d < t - timedelta(days=past_days):
        raise ValueError(f"{day} looks wrong: today is {today()} (India). Use a date near today, "
                         "or leave the date empty to mean today / this month.")
    return day


def phone(raw: str) -> str:
    """Normalise any phone format to +<digits> (WhatsApp sends '919876543210')."""
    digits = re.sub(r"\D", "", raw)
    return f"+{digits}" if digits else ""


# --- Who is asking ---------------------------------------------------------
# Every query is scoped to one user: WhatsApp sets the sender per message, the
# dashboard API sets it from the session. Tools never take the user as an
# argument, so the model can't reach anyone else's data.

_user: ContextVar[str | None] = ContextVar("spenzo_user", default=None)


def current_user() -> str:
    return _user.get() or "local"   # "local": the terminal simulator before a number is set


def set_user(raw_phone: str) -> None:
    _user.set(phone(raw_phone) or raw_phone)
