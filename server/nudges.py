"""Well-timed nudges: at most one per reply, each sent once per period.

Nudges only ride along on replies to something the user just did, so they're
free on WhatsApp and never arrive out of nowhere. Priority, highest first:
over budget > nearly over > spending too fast > payday > last month's Wrapped > goal behind >
friend overdue > one-time tips that introduce a feature when it's useful.
"""
from datetime import date, timedelta

from server import auth, db, profile, save, spend, split
from server.core import current_user, today
from server.replies import Reply, inr

OVERDUE_DAYS = 14


def _month() -> str:
    return today()[:7]


def once(key: str, period: str) -> bool:
    """True the first time (key, period) is seen for this user, and records it."""
    return db.row("insert into nudges_sent (phone, key, period) values (%s, %s, %s) "
                  "on conflict do nothing returning key", current_user(), key, period) is not None


def _expense_count() -> int:
    return db.value("select count(*) from transactions where phone = %s and kind = 'expense'", current_user())


def _budget_nudges(events: set[str]) -> Reply | None:
    if "expense" not in events:
        return None
    statuses = spend.budget_status()
    day = date.fromisoformat(today()).day
    for b in sorted(statuses, key=lambda b: -b["used_pct"]):
        name = "Overall" if b["category"] == spend.TOTAL else b["category"]
        if b["used_pct"] >= 100:
            if once(f"budget100:{b['category']}", _month()):
                return Reply(f"🚨 {name} budget is used up ({inr(b['spent'])} of {inr(b['limit'])}), "
                             f"{b['days_left']} days to go.")
            continue
        if b["used_pct"] >= 80 and once(f"budget80:{b['category']}", _month()):
            return Reply(f"😬 {name} is at {b['used_pct']}% of {inr(b['limit'])}, {inr(b['left'])} left for {b['days_left']} days.")
        if (8 <= day <= 22 and b["used_pct"] < 80 and b["projected"] > b["limit"] * 1.1
                and once(f"pace:{b['category']}", _month())):
            per_day = max(b["left"], 0) / max(b["days_left"], 1)
            return Reply(f"🤔 At this pace {name.lower()} lands near {inr(b['projected'])}. "
                         f"About {inr(per_day)} a day keeps you under {inr(b['limit'])}.")
    return None


def _payday(events: set[str]) -> Reply | None:
    if "salary" not in events:
        return None
    goals = [g for g in save.goals_status() if g["left"] > 0]
    if not goals:
        if once("tip:goal", "once"):
            return Reply("💸 Saving up for anything? Tell me like *Goa trip 30k by March* and I'll keep you on track.")
        return None
    g = goals[0]
    amount = round(g.get("per_month_needed") or min(g["left"], 5000))
    if once(f"payday:{g['name']}", _month()):
        return Reply(f"💸 Payday! Move {inr(amount)} to {g['name']}? That keeps it on track.",
                     buttons=[(f"goalmove:{g['name']}:{amount}", f"Move {inr(amount)}"), ("ok", "Not now")])
    return None


def _wrapped() -> Reply | None:
    """Early in a month, offer last month's Wrapped card once."""
    now = date.fromisoformat(today())
    if now.day > 10:
        return None
    last = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
    count = db.value("select count(*) from transactions where phone = %s and kind = 'expense' and "
                     "date >= %s and date < %s", current_user(), last.isoformat(), now.replace(day=1).isoformat())
    if count >= 10 and once("wrapped", last.strftime("%Y-%m")):
        return Reply(f"🎁 Your {last.strftime('%B')} Wrapped is ready.",
                     buttons=[(f"wrapped:{last.strftime('%Y-%m')}", "🎁 Open Wrapped"), ("ok", "Later")])
    return None


def _goal_behind() -> Reply | None:
    for g in save.goals_status():
        if g.get("behind_by", 0) > 0 and once(f"behind:{g['name']}", _month()):
            return Reply(f"🎯 {g['name']} is {inr(g['behind_by'])} behind. "
                         f"{inr(g['per_month_needed'])} a month still gets you there.")
    return None


def _overdue_friend() -> Reply | None:
    for p in split.list_debts()["they_owe_you"]:
        days = (date.fromisoformat(today()) - date.fromisoformat(str(p["since"]))).days
        if days >= OVERDUE_DAYS and once(f"overdue:{p['person'].lower()}:{p['since']}", "once"):
            return Reply(f"👀 {p['person']} has owed you {inr(p['net'])} for {days} days. "
                         "Send me your UPI ID and I'll make a link you can forward.")
    return None


def _tips(events: set[str]) -> Reply | None:
    if "expense" in events and _expense_count() >= 3 and once("tip:dashboard", "once"):
        return Reply("Want to see where it's all going?", link=("📊 Open dashboard", auth.dashboard_url()))
    if "expense" in events and _expense_count() >= 15 and not spend.budget_status() and once("tip:budget", "once"):
        top = spend.summarize()["by_category"]
        if top:
            cat = top[0]["category"]
            typical = spend.typical_month(cat) or top[0]["total"] * 2
            limit = int(round(typical * 0.9, -2)) or 1000
            return Reply(f"🎯 {cat} is your biggest spend. Cap it at {inr(limit)} a month?",
                         buttons=[(f"budget:{cat}:{limit}", f"Set {inr(limit)}"), ("ok", "Not now")])
    return None


def next_nudge(events: set[str]) -> Reply | None:
    """The single most useful nudge after the user did `events` ('expense', 'salary', 'debt', 'goal')."""
    if not events:
        return None
    user = profile.get()
    if user and user.get("nudges") is False:
        return None
    for check in (lambda: _budget_nudges(events), lambda: _payday(events), _wrapped, _goal_behind,
                  _overdue_friend, lambda: _tips(events)):
        nudge = check()
        if nudge:
            return nudge
    return None
