"""What Spenzo sends back: text plus up to 3 buttons or one link button, and optionally a
reaction on the user's message, a Baaz sticker or a generated picture.

Also the replies that need no AI at all: welcome, help, undo, and every button press
(Undo, This month, Set budget…), so taps answer instantly.
"""
import re
from dataclasses import dataclass, field
from datetime import date

from server import auth, brand, db, profile, save, spend, split
from server.core import current_user


@dataclass
class Reply:
    text: str
    buttons: list[tuple[str, str]] = field(default_factory=list)   # (id, title) · max 3, title ≤ 20 chars
    link: tuple[str, str] | None = None                            # (label, url) · shown as a button
    image: str = ""                                                # public image URL shown above the text
    then: "Reply | None" = None                                    # an optional second message
    react: str = ""                                                # emoji reaction on the user's message
    sticker: str = ""                                              # Baaz sticker sent after the text: "celebrate"
    png: bytes | None = None                                       # a generated picture, with the text as caption
    logged: float = 0                                              # a plain log of this amount: may go out as just a ✅


def inr(amount: float) -> str:
    """₹1,23,456.50: Indian digit grouping, no trailing .00."""
    sign = "-" if amount < 0 else ""
    whole, _, paise = f"{abs(amount):.2f}".partition(".")
    head, tail = whole[:-3], whole[-3:]
    whole = f"{re.sub(r'(\d)(?=(\d\d)+$)', r'\1,', head)},{tail}" if head else tail
    return f"{sign}₹{whole}" + ("" if paise == "00" else f".{paise}")


def whatsapp_format(text: str) -> str:
    """Models write Markdown; WhatsApp bolds with single asterisks and shows raw URLs."""
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1: \2", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    return re.sub(r" +\n", "\n", text).strip()


def logged(e: dict) -> Reply:
    what = e["description"] or e["category"]
    note = f"\n_{e['note']}_" if e.get("note") else ""
    return Reply(f"✅ {inr(e['amount'])} · {what} / {e['category']}{note}",
                 buttons=[(f"undo:{e['id']}", "↩️ Undo"), (f"edit:{e['id']}", "✏️ Edit"), ("month", "📊 This month")],
                 logged=e["amount"])


def goal_sticker(goal: dict, added: float) -> str:
    """Baaz cheers when a top-up crosses halfway or finishes a goal."""
    if added <= 0 or not goal.get("target"):
        return ""
    before = 100 * (goal["saved"] - added) / goal["target"]
    if before < 100 <= goal["pct"]:
        return "celebrate"
    if before < 50 <= goal["pct"]:
        return "grow"
    return ""


# --- No-AI replies ---------------------------------------------------------------


def undo_last() -> Reply:
    """Remove the user's most recent transaction ("undo", "delete that")."""
    last = db.row("select id from transactions where phone = %s and source is null "
                  "and created_at > now() - interval '1 day' order by id desc limit 1", current_user())
    if not last:
        return Reply("Nothing recent to undo.")
    gone = spend.delete_transaction(last["id"])["deleted"]
    return Reply(f"↩️ Removed {inr(gone['amount'])} · {gone['description'] or gone['category']}.")


def welcome(name: str) -> Reply:
    hi = f"Hi {name.split()[0]}!" if name else "Hi!"
    return Reply(
        f"👋 {hi} I'm {brand.NAME}, your money buddy.\n\n"
        "Just tell me what you spend, like *chai 20* or *uber 250*. "
        "Photos of bills and voice notes work too.",
        buttons=[("help", "What else?")],
        image=f"{brand.WEB_URL}/mascot/baaz-welcome.jpg",
    )


def help_menu() -> Reply:
    return Reply(
        "Here's what I can do. Just ask in your own words:\n\n"
        "💸 *Spend*: \"food 450\", \"salary 60k\", \"keep food under 6k\"\n"
        "🤝 *Split*: \"dinner 3000 split with Arav and Riya\", \"I owe Kabir 200\"\n"
        "🎯 *Save*: \"Goa trip 30k by March\", \"I have 10 TCS shares\"\n"
        "📊 *See*: \"where did my money go?\", \"Swiggy this year vs last\"\n"
        "📄 *Forward*: a bank statement PDF, a payment screenshot, or a bill from any chat",
        buttons=[("month", "📊 This month"), ("debts", "🤝 Who owes me"), ("goals", "🎯 My goals")],
    )


def month_view() -> Reply:
    m = spend.summarize()
    name = date.fromisoformat(m["from"]).strftime("%B")
    if not m["count"]:
        return Reply(f"Nothing logged in {name} yet. Tell me your first spend, like *lunch 180*.")
    top = " · ".join(f"{c['category']} {inr(c['total'])}" for c in m["by_category"][:4])
    lines = [f"📊 *{name} so far: {inr(m['spent'])}*", top]
    if m["income"]:
        lines.append(f"Income {inr(m['income'])} · left {inr(m['left'])}")
    for b in spend.budget_status():
        if b["used_pct"] >= 80:
            lines.append(f"⚠️ {b['category']} budget {b['used_pct']}% used")
    return Reply("\n".join(lines), link=("📊 See everything", auth.dashboard_url()))


def debts_view() -> Reply:
    d = split.list_debts()
    if not d["they_owe_you"] and not d["you_owe"]:
        return Reply("All square 🤝 Nobody owes anybody.")
    lines = [f"• {p['person']} owes you {inr(p['net'])}" for p in d["they_owe_you"]]
    lines += [f"• You owe {p['person']} {inr(p['net'])}" for p in d["you_owe"]]
    if d["they_owe_you"]:
        lines.append("\nSend me your UPI ID and I'll make tap-to-pay links to forward.")
    return Reply("🤝 *Who owes what*\n" + "\n".join(lines))


def goals_view() -> Reply:
    goals = save.goals_status()
    if not goals:
        return Reply("No goals yet. Tell me one, like *Goa trip 30k by March*.")
    lines = []
    for g in goals:
        line = f"• {g['name']}: {inr(g['saved'])} of {inr(g['target'])} ({g['pct']}%)"
        if g.get("per_month_needed"):
            line += f", {inr(g['per_month_needed'])}/month to make it"
        lines.append(line)
    return Reply("🎯 *Your goals*\n" + "\n".join(lines))


def press(button_id: str) -> Reply:
    """Handle a tapped button without calling the AI."""
    action, _, arg = button_id.partition(":")
    if action == "undo":
        gone = spend.delete_transaction(int(arg))["deleted"]
        return Reply(f"↩️ Removed {inr(gone['amount'])} · {gone['description'] or gone['category']}.")
    if action == "edit":
        return Reply("What should it be? Like *make it 500* or *it was Rapido*.")
    if action == "month":
        return month_view()
    if action == "debts":
        return debts_view()
    if action == "goals":
        return goals_view()
    if action == "help":
        return help_menu()
    if action == "budget":
        category, amount = arg.rsplit(":", 1)
        spend.set_budget(category, float(amount))
        return Reply(f"🎯 {category} budget set to {inr(float(amount))} a month. I'll tell you at 80%.")
    if action == "goalmove":
        goal, amount = arg.rsplit(":", 1)
        g = save.add_to_goal(goal, float(amount))
        return Reply(f"🎯 {inr(float(amount))} moved to {g['name']}. You're at {g['pct']}%.",
                     sticker=goal_sticker(g, float(amount)))
    if action == "undo_import":
        n = db.value("with gone as (delete from transactions where phone = %s and source = %s returning 1) "
                     "select count(*) from gone", current_user(), arg)
        return Reply(f"↩️ Removed the {n} transactions from that statement." if n else "That import is already gone.")
    if action == "wrapped":
        from server import insights   # imports replies, so load it on demand
        return insights.wrapped_reply(arg)
    if action == "nudges_off":
        profile.set_nudges(False)
        return Reply("Okay, no more nudges. Say *turn nudges on* anytime.")
    if action == "delete_all":
        if arg == "yes":
            profile.delete_everything()
            return Reply("Done. Everything is deleted. Say hi anytime to start fresh.")
        return Reply("Cancelled. Nothing was deleted.")
    if action == "ok":
        return Reply("👍")
    return Reply("That button has expired. Just tell me what you need.")
