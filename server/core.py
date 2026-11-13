"""Shared plumbing: settings, the current user, dates and HTTP."""
import calendar
import os
import re
from contextvars import ContextVar
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

IST = timezone(timedelta(hours=5, minutes=30))
LINK_FILE = Path.home() / ".spenzo" / "linked_phone"

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


def phone(raw: str) -> str:
    """Normalise any phone format to +<digits> (WhatsApp sends '919876543210')."""
    digits = re.sub(r"\D", "", raw)
    return f"+{digits}" if digits else ""


# --- Who is asking ---------------------------------------------------------
# Every query is scoped to one user. WhatsApp sets the sender per message;
# Claude Desktop uses the WhatsApp number linked on this machine, or "local".
# Tools never take the user as an argument, so the model can't reach anyone
# else's data.

_user: ContextVar[str | None] = ContextVar("spenzo_user", default=None)


def linked_phone() -> str:
    if env("LINKED_PHONE"):
        return env("LINKED_PHONE")
    if LINK_FILE.exists():
        return LINK_FILE.read_text().strip()
    return ""


def current_user() -> str:
    return _user.get() or linked_phone() or "local"


def set_user(raw_phone: str) -> None:
    _user.set(phone(raw_phone) or raw_phone)
