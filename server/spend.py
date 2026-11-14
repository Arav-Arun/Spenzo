"""Spend: money in and out, and monthly budgets."""
from datetime import date

from server import db
from server.core import check_date, current_user, month_range, today
from server.markets import to_inr

CATEGORIES = {
    "Food & Dining": "groceries, restaurants, coffee, delivery",
    "Transport": "cabs, auto, metro, fuel, flights",
    "Shopping": "clothes, electronics, online orders",
    "Bills & Rent": "rent, electricity, phone, internet",
    "Entertainment": "movies, events, subscriptions, games",
    "Health": "medicine, doctor, gym",
    "Education": "courses, books, fees",
    "Travel": "trips, hotels",
    "Other": "gifts, personal care, anything else",
}
TOTAL = "Total"  # a budget on all spending
FIELDS = "id, date, kind, amount, category, description, note, tags"
EDITABLE = ("amount", "category", "description", "note", "date", "tags")


def _clean_tags(tags: list[str] | None) -> list[str]:
    return sorted({t.strip().lower().lstrip("#") for t in tags or [] if t.strip()})


def _record(kind: str, amount: float, category: str, description: str, note: str,
            day: str, currency: str, tags: list[str] | None) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be more than zero.")
    if day:
        check_date(day)
    if currency.upper() not in ("INR", "₹", "RS"):
        original = f"{amount:g} {currency.upper()}"
        amount, per_unit = to_inr(amount, currency)
        note = "; ".join(filter(None, [note, f"{original} at ₹{per_unit:,.2f}"]))
    return db.row(
        f"insert into transactions (phone, date, kind, amount, category, description, note, tags) "
        f"values (%s, %s, %s, %s, %s, %s, %s, %s) returning {FIELDS}",
        current_user(), day or today(), kind, round(amount, 2), category,
        description.strip(), note.strip(), _clean_tags(tags))


def add_expense(amount: float, category: str, description: str = "", date: str = "",
                currency: str = "INR", tags: list[str] | None = None, note: str = "") -> dict:
    """Log money the user spent. Pick the closest category yourself: Food & Dining, Transport,
    Shopping, Bills & Rent, Entertainment, Health, Education, Travel or Other. description is
    what it was ("Uber", "Samosa chaat"). tags: merchant, trip or person names in lowercase
    (["zomato"], ["goa trip"]). date YYYY-MM-DD, default today. Foreign money: pass the original
    amount and currency (USD, EUR…), never convert it yourself. Split bill: pass only the user's share."""
    return _record("expense", amount, category, description, note, date, currency, tags)


def add_income(amount: float, category: str = "Salary", description: str = "", date: str = "",
               currency: str = "INR") -> dict:
    """Log money the user received: Salary, Freelance, Pocket money, Refund, Gift or Other income."""
    return _record("income", amount, category, description, "", date, currency, None)


def summarize(start_date: str = "", end_date: str = "") -> dict:
    """Money in and out between two dates (YYYY-MM-DD, inclusive): total spent, spending by
    category, income, and what's left. Leave both dates empty for the current month: the result
    includes today's date, so don't guess dates from your own knowledge."""
    start, end = (start_date, end_date) if start_date and end_date else month_range()
    check_date(start), check_date(end, future_days=366)
    groups = db.rows(
        "select kind, category, sum(amount) as total, count(*) as n from transactions "
        "where phone = %s and date between %s and %s group by kind, category order by total desc",
        current_user(), start, end)
    spent = [g for g in groups if g["kind"] == "expense"]
    income = sum(g["total"] for g in groups if g["kind"] == "income")
    total = sum(g["total"] for g in spent)
    return {
        "today": today(), "from": start, "to": end, "spent": round(total, 2), "income": round(income, 2),
        "left": round(income - total, 2) if income else None,
        "by_category": [{"category": g["category"], "total": round(g["total"], 2)} for g in spent],
        "count": sum(g["n"] for g in spent),
    }


def list_transactions(start_date: str = "", end_date: str = "", kind: str = "expense") -> list[dict]:
    """Every expense (or income, kind='income') between two dates (YYYY-MM-DD), oldest first.
    Leave both dates empty for the current month."""
    if not (start_date and end_date):
        start_date, end_date = month_range()
    check_date(start_date), check_date(end_date, future_days=366)
    return db.rows(f"select {FIELDS} from transactions where phone = %s and kind = %s "
                   "and date between %s and %s order by date, id", current_user(), kind, start_date, end_date)


def search_transactions(query: str) -> list[dict]:
    """Find the user's transactions by keyword (newest 20). Use this to get the id before
    editing or deleting."""
    term = query.strip().lower()
    if not term.strip("*%_ "):
        return []
    like = "%" + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    return db.rows(f"select {FIELDS} from transactions where phone = %s and "
                   "(description ilike %s or note ilike %s or category ilike %s or %s = any(tags)) "
                   "order by date desc, id desc limit 20", current_user(), like, like, like, term)


def edit_transaction(transaction_id: int, amount: float | None = None, category: str | None = None,
                     description: str | None = None, note: str | None = None, date: str | None = None,
                     tags: list[str] | None = None) -> dict:
    """Change one of the user's transactions. Pass only what changes."""
    given = {"amount": amount, "category": category, "description": description, "note": note, "date": date}
    changes = {k: v for k, v in given.items() if v is not None}
    if tags is not None:
        changes["tags"] = _clean_tags(tags)
    if date is not None:
        check_date(date)
    if not changes:
        raise ValueError("Nothing to change.")
    sets = ", ".join(f"{col} = %s" for col in changes if col in EDITABLE)
    updated = db.row(f"update transactions set {sets} where id = %s and phone = %s returning {FIELDS}",
                     *changes.values(), transaction_id, current_user())
    if not updated:
        raise ValueError(f"No transaction #{transaction_id} in your ledger.")
    return updated


def delete_transaction(transaction_id: int) -> dict:
    """Delete one of the user's transactions."""
    gone = db.row(f"delete from transactions where id = %s and phone = %s returning {FIELDS}",
                  transaction_id, current_user())
    if not gone:
        raise ValueError(f"No transaction #{transaction_id} in your ledger.")
    return {"deleted": gone}


# --- Budgets -----------------------------------------------------------------


def set_budget(category: str, monthly_limit: float) -> dict:
    """Set a monthly spending limit for a category, or for all spending with category 'Total'.
    A limit of 0 removes it."""
    if monthly_limit <= 0:
        db.execute("delete from budgets where phone = %s and category = %s", current_user(), category)
        return {"removed": category}
    db.execute("insert into budgets (phone, category, monthly_limit) values (%s, %s, %s) "
               "on conflict (phone, category) do update set monthly_limit = excluded.monthly_limit",
               current_user(), category, round(monthly_limit, 2))
    return budget_status(category)[0]


def budget_status(category: str = "") -> list[dict]:
    """This month's spending against each budget, with where the month is heading."""
    budgets = db.rows("select category, monthly_limit from budgets where phone = %s and (%s = '' or category = %s) "
                      "order by category", current_user(), category, category)
    if not budgets:
        return []
    month = summarize()
    by_category = {c["category"]: c["total"] for c in month["by_category"]}
    day, days_in_month = date.fromisoformat(today()).day, date.fromisoformat(month["to"]).day
    out = []
    for b in budgets:
        spent = month["spent"] if b["category"] == TOTAL else by_category.get(b["category"], 0)
        limit = b["monthly_limit"]
        out.append({"category": b["category"], "limit": limit, "spent": round(spent, 2),
                    "left": round(limit - spent, 2), "used_pct": round(100 * spent / limit),
                    "projected": round(spent / day * days_in_month), "days_left": days_in_month - day})
    return out


def typical_month(category: str) -> float | None:
    """Average monthly spend in a category over the last 3 full months."""
    first_of_month = month_range()[0]
    avg = db.value(
        "select avg(total) from (select date_trunc('month', date) as m, sum(amount) as total from transactions "
        "where phone = %s and kind = 'expense' and category = %s "
        "and date >= %s::date - interval '3 months' and date < %s::date group by 1) months",
        current_user(), category, first_of_month, first_of_month)
    return round(avg) if avg else None
