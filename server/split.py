"""Split: who owes whom, in both directions, with UPI links to collect."""
import re
from urllib.parse import urlencode

from server import brand, db
from server.core import current_user, today

UPI_ID = re.compile(r"^[\w.\-]{2,256}@[A-Za-z]{2,64}$")
DIRECTIONS = ("they_owe", "i_owe")
# Stand-ins a model might invent when the user didn't say who: never store these.
PLACEHOLDER = re.compile(r"^(friend|person|someone|somebody|unknown|other|guest|people|friends)\s*\d*$", re.I)


def _name(person: str) -> str:
    """A person's name as people write it: "kabir" -> "Kabir", "DJ" stays "DJ"."""
    person = " ".join(person.split())
    if PLACEHOLDER.match(person):
        raise ValueError("The user didn't say who this is. Ask them for the person's name; don't make one up.")
    return person.title() if person.islower() else person


def pay_link(upi_id: str, amount: float, note: str = "") -> str:
    """A web page that opens any UPI app with the payment filled in
    (WhatsApp doesn't make raw upi:// links tappable)."""
    if not UPI_ID.match(upi_id.strip()):
        raise ValueError(f"'{upi_id}' doesn't look like a UPI ID (like name@okicici).")
    params = {"pa": upi_id.strip(), "am": f"{amount:.2f}", "tn": note[:50]}
    return f"{brand.WEB_URL}/pay?{urlencode(params)}"


def balance(person: str) -> dict:
    """Net position with one person: positive = they owe the user."""
    found = db.row("select (array_agg(person order by date, id))[1] as person, coalesce(sum(case when direction = 'they_owe' then amount "
                   "else -amount end), 0) as net from debts where phone = %s and lower(person) = lower(%s)",
                   current_user(), person.strip())
    return {"person": found["person"] or person.strip(), "net": round(found["net"], 2)}


def log_debt(person: str, amount: float, reason: str = "", direction: str = "they_owe") -> dict:
    """Record money owed. direction 'they_owe' = the person owes the user ("Arav owes me 500");
    'i_owe' = the user owes them ("I owe Riya 300"). For a split bill, log the user's own share
    with add_expense and each other person's share here."""
    if direction not in DIRECTIONS:
        raise ValueError("direction must be 'they_owe' or 'i_owe'.")
    if amount <= 0:
        raise ValueError("Amount must be more than zero.")
    person = _name(person)
    db.execute("insert into debts (phone, person, direction, amount, reason, date) values (%s, %s, %s, %s, %s, %s)",
               current_user(), person, direction, round(amount, 2), reason, today())
    return {"person": person, "direction": direction, "logged": round(amount, 2), "balance": balance(person)}


def list_debts(upi_id: str = "") -> dict:
    """Everyone the user owes or who owes the user, netted per person, oldest first.
    If the user shares their UPI ID, each person who owes them gets a tap-to-pay link."""
    people = db.rows(
        "select (array_agg(person order by date, id))[1] as person, "
        "sum(case when direction = 'they_owe' then amount else -amount end) as net, "
        "array_remove(array_agg(nullif(reason, '') order by date, id), null) as reasons, min(date) as since "
        "from debts where phone = %s group by lower(person) order by min(date)", current_user())
    people = [{"person": p["person"], "net": p["net"], "for": p["reasons"], "since": p["since"]} for p in people]
    owed = [p | {"net": round(p["net"], 2)} for p in people if p["net"] > 0]
    owing = [p | {"net": round(-p["net"], 2)} for p in people if p["net"] < 0]
    if upi_id:
        for p in owed:
            p["pay_link"] = pay_link(upi_id, p["net"], ", ".join(p["for"]) or "Spenzo")
    return {
        "they_owe_you": sorted(owed, key=lambda p: -p["net"]), "you_owe": sorted(owing, key=lambda p: -p["net"]),
        "total_owed_to_you": round(sum(p["net"] for p in owed), 2), "total_you_owe": round(sum(p["net"] for p in owing), 2),
        **({"tip": "Offer tap-to-pay links if they share their UPI ID."} if owed and not upi_id else {}),
    }


def settle_debt(person: str, amount: float | None = None, direction: str = "they_owe") -> dict:
    """Mark money as paid. direction 'they_owe' = the person paid the user back;
    'i_owe' = the user paid them. No amount clears it all; otherwise oldest first."""
    with db.transaction():
        debts = db.rows("select id, amount from debts where phone = %s and lower(person) = lower(%s) "
                        "and direction = %s order by date, id for update", current_user(), person.strip(), direction)
        if not debts:
            who = f"{person} doesn't owe you anything" if direction == "they_owe" else f"You don't owe {person} anything"
            raise ValueError(f"{who}.")
        remaining = sum(d["amount"] for d in debts) if amount is None else amount
        for d in debts:
            if remaining <= 0:
                break
            if d["amount"] <= remaining:
                db.execute("delete from debts where id = %s", d["id"])
            else:
                db.execute("update debts set amount = %s where id = %s", round(d["amount"] - remaining, 2), d["id"])
            remaining -= d["amount"]
    return balance(person)
