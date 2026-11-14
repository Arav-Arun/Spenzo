"""The user: profile, long-term memory, chat history, privacy controls."""
from datetime import timedelta

from server import db
from server.core import current_user, now

HISTORY_MESSAGES = 10   # last 5 exchanges
HISTORY_HOURS = 6
MAX_FACTS = 30
USER_TABLES = ["transactions", "budgets", "debts", "goals", "holdings", "messages", "nudges_sent"]


def get() -> dict | None:
    return db.row("select * from users where phone = %s", current_user())


def ensure(name: str = "") -> tuple[dict, bool]:
    """The user's row, creating it on first contact. Returns (user, is_new)."""
    created = db.row("insert into users (phone, name) values (%s, %s) on conflict (phone) do nothing returning *",
                     current_user(), name.strip())
    return (created, True) if created else (get(), False)


def remember(fact: str = "", name: str = "", monthly_income: float = 0, salary_day: int = 0) -> dict:
    """Save something worth knowing next time: the user's name, monthly income, salary day
    (1–31), or a short fact ("Riya is my flatmate", "saving for a bike"). Use it whenever the
    user tells you something like this; don't ask permission."""
    user, _ = ensure()
    facts = user["facts"] or []
    if fact.strip():
        facts = ([f for f in facts if f.lower() != fact.strip().lower()] + [fact.strip()])[-MAX_FACTS:]
    saved = db.row(
        "update users set name = coalesce(nullif(%s, ''), name), monthly_income = coalesce(%s, monthly_income), "
        "salary_day = coalesce(%s, salary_day), facts = %s where phone = %s "
        "returning name, monthly_income, salary_day, facts",
        name.strip(), round(monthly_income, 2) if monthly_income > 0 else None,
        salary_day if 1 <= salary_day <= 31 else None, db.Jsonb(facts), current_user())
    return saved


def forget(fact: str) -> dict:
    """Forget a saved fact."""
    user, _ = ensure()
    facts = [f for f in user["facts"] or [] if fact.lower() not in f.lower()]
    return db.row("update users set facts = %s where phone = %s returning facts", db.Jsonb(facts), current_user())


def set_nudges(on: bool) -> dict:
    """Turn Spenzo's nudges (budget warnings, goal reminders, tips) on or off."""
    ensure()
    return db.row("update users set nudges = %s where phone = %s returning nudges", on, current_user())


def sign_out_everywhere() -> dict:
    """Sign out of the Spenzo dashboard on every browser."""
    ensure()
    return db.row("update users set session_version = session_version + 1 where phone = %s "
                  "returning session_version", current_user())


def delete_everything() -> dict:
    """Permanently delete all of this user's data. Only called after the user taps the confirm button."""
    with db.transaction():
        for table in USER_TABLES + ["users"]:
            db.execute(f"delete from {table} where phone = %s", current_user())
    return {"deleted": True}


# --- Chat memory ---------------------------------------------------------------


def history() -> list[dict]:
    recent = db.rows("select role, content from messages where phone = %s and created_at >= %s "
                     "order by created_at desc, id desc limit %s",
                     current_user(), now() - timedelta(hours=HISTORY_HOURS), HISTORY_MESSAGES)
    return list(reversed(recent))


def save_exchange(said: str, answer: str) -> None:
    with db.transaction():
        db.execute("insert into messages (phone, role, content) values (%s, 'user', %s), (%s, 'assistant', %s)",
                   current_user(), said, current_user(), answer)
        # Keep a week of chat at most; older context isn't used.
        db.execute("delete from messages where phone = %s and created_at < %s", current_user(), now() - timedelta(days=7))
