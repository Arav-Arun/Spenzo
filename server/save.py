"""Save: goals, investments (stocks and mutual funds) and net worth.

Spenzo reports facts about a portfolio and never recommends buying or selling.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from server import db, markets
from server.core import check_date, current_user, today

FUND_WORDS = ("fund", "flexi cap", "large cap", "mid cap", "small cap", "elss", "index", "direct", "growth")

# --- Goals -------------------------------------------------------------------


def _goal(name: str) -> dict:
    found = db.row("select * from goals where phone = %s and name ilike %s order by created_at limit 1",
                   current_user(), f"%{name.strip()}%")
    if not found:
        names = ", ".join(g["name"] for g in _goals()) or "none yet"
        raise ValueError(f"No goal called '{name}'. Your goals: {names}.")
    return found


def _goals() -> list[dict]:
    return db.rows("select * from goals where phone = %s order by created_at, id", current_user())


def _progress(g: dict) -> dict:
    out = {"name": g["name"], "target": g["target"], "saved": g["saved"],
           "pct": round(100 * g["saved"] / g["target"]), "left": round(max(g["target"] - g["saved"], 0), 2),
           "deadline": g["deadline"]}
    if g["deadline"] and g["saved"] < g["target"]:
        start = date.fromisoformat(str(g["created_at"])[:10])
        end, now = date.fromisoformat(g["deadline"]), date.fromisoformat(today())
        months_left = max((end.year - now.year) * 12 + end.month - now.month, 1)
        out["per_month_needed"] = round(out["left"] / months_left)
        expected = g["target"] * min(max((now - start).days / max((end - start).days, 1), 0), 1)
        out["behind_by"] = round(max(expected - g["saved"], 0))
    return out


def add_goal(name: str, target: float, deadline: str = "") -> dict:
    """Start a savings goal ("Goa trip, ₹30,000 by March"). deadline YYYY-MM-DD, optional."""
    if target <= 0:
        raise ValueError("Target must be more than zero.")
    if deadline:
        check_date(deadline, future_days=365 * 30, past_days=0)
    return _progress(db.row("insert into goals (phone, name, target, deadline, created_at) "
                            "values (%s, %s, %s, %s, %s) returning *",
                            current_user(), name.strip(), round(target, 2), deadline or None, today()))


def add_to_goal(name: str, amount: float) -> dict:
    """Put money toward a goal (use a negative amount to take money out)."""
    g = _goal(name)
    return _progress(db.row("update goals set saved = greatest(saved + %s, 0) where id = %s returning *",
                            round(amount, 2), g["id"]))


def goals_status() -> list[dict]:
    """Every goal with progress, and how much a month keeps it on track."""
    return [_progress(g) for g in _goals()]


def delete_goal(name: str) -> dict:
    """Remove a goal (reached or no longer wanted)."""
    g = _goal(name)
    db.execute("delete from goals where id = %s", g["id"])
    return {"deleted": g["name"]}


# --- Investments ---------------------------------------------------------------


def add_investment(name: str, quantity: float, avg_price: float = 0, kind: str = "auto") -> dict:
    """Add or update a holding. name is a company ("TCS", "Reliance") or a mutual fund
    ("Parag Parikh Flexi Cap"). quantity is shares or units; avg_price what the user paid per
    share or unit, if they know it. kind: 'stock', 'mutual_fund' or 'auto' (guess from the name).
    Use this for each row when the user sends a screenshot of their Groww/Zerodha/Upstox holdings."""
    if quantity <= 0:
        raise ValueError("Quantity must be more than zero.")
    if kind == "auto":
        kind = "mutual_fund" if any(w in name.lower() for w in FUND_WORDS) else "stock"
    found = markets.find_fund(name) if kind == "mutual_fund" else markets.find_stock(name)
    db.execute("insert into holdings (phone, kind, symbol, name, quantity, avg_price) values (%s, %s, %s, %s, %s, %s) "
               "on conflict (phone, kind, symbol) do update set quantity = excluded.quantity, "
               "avg_price = excluded.avg_price, name = excluded.name",
               current_user(), kind, found["symbol"], found["name"], quantity, avg_price or None)
    return {"added": found["name"], "kind": kind, "quantity": quantity}


def remove_investment(name: str) -> dict:
    """Stop tracking a holding (sold, or added by mistake)."""
    gone = db.row("delete from holdings where id = (select id from holdings where phone = %s and "
                  "(name ilike %s or symbol ilike %s) order by created_at limit 1) returning name",
                  current_user(), f"%{name}%", f"%{name}%")
    if not gone:
        raise ValueError(f"No holding matching '{name}'.")
    return {"removed": gone["name"]}


def _price(h: dict) -> dict:
    try:
        quote = markets.fund_nav(h["symbol"]) if h["kind"] == "mutual_fund" else markets.stock_price(h["symbol"])
        prev = quote.get("previous_close")
        return {"value": round(quote["price"] * h["quantity"], 2),
                "invested": round(h["avg_price"] * h["quantity"], 2) if h["avg_price"] else None,
                "day_change_pct": round(100 * (quote["price"] / prev - 1), 2) if prev else None}
    except Exception as e:  # one bad symbol shouldn't sink the whole report
        return {"value": 0, "invested": None, "error": str(e)}


def portfolio() -> dict:
    """The user's investments right now: value, gain, mix and plain facts (biggest holding,
    concentration). Facts only: never suggest buying or selling anything."""
    holdings = db.rows("select * from holdings where phone = %s order by created_at, id", current_user())
    if not holdings:
        return {"holdings": [], "facts": [], "mix_pct": {},
                "tip": "Add holdings by name, or send a screenshot of your broker's holdings page."}
    with ThreadPoolExecutor(max_workers=8) as pool:
        priced = [h | p for h, p in zip(holdings, pool.map(_price, holdings))]
    total = sum(h["value"] for h in priced)
    with_cost = [h for h in priced if h.get("invested")]
    invested = sum(h["invested"] for h in with_cost)
    gain = sum(h["value"] for h in with_cost) - invested
    mix: dict[str, float] = {}
    for h in priced:
        mix[h["kind"]] = mix.get(h["kind"], 0) + h["value"]
    listed = sorted(({"name": h["name"], "kind": h["kind"], "value": h["value"],
                      "share_pct": round(100 * h["value"] / total) if total else 0,
                      **({"gain_pct": round(100 * (h["value"] / h["invested"] - 1), 1)} if h.get("invested") else {}),
                      **({"today_pct": h["day_change_pct"]} if h.get("day_change_pct") is not None else {}),
                      **({"error": h["error"]} if h.get("error") else {})} for h in priced), key=lambda r: -r["value"])
    facts = []
    if len(listed) > 1 and listed[0]["share_pct"] >= 30:
        facts.append(f"{listed[0]['name']} is {listed[0]['share_pct']}% of the portfolio.")
    return {
        "value": round(total, 2),
        "gain_on_holdings_with_known_cost": {
            "holdings": [h["name"] for h in with_cost], "invested": round(invested, 2),
            "now_worth": round(invested + gain, 2), "gain": round(gain, 2),
            "gain_pct": round(100 * gain / invested, 1) if invested else None,
        } if with_cost else None,
        "mix_pct": {k: round(100 * v / total) for k, v in mix.items()} if total else {},
        "holdings": listed, "facts": facts,
        "note": "Prices can be up to 15 minutes old. Mutual fund values use the latest published NAV.",
    }


def net_worth() -> dict:
    """Everything the user owns minus what they owe: goal savings + investments +
    money friends owe them − money they owe friends."""
    from server.split import list_debts
    debts = list_debts()
    parts = {"goal_savings": round(sum(g["saved"] for g in _goals()), 2),
             "investments": portfolio().get("value", 0),
             "owed_to_you": debts["total_owed_to_you"], "you_owe": -debts["total_you_owe"]}
    return {"net_worth": round(sum(parts.values()), 2), **parts,
            "note": "Bank balances aren't included unless saved toward a goal."}
