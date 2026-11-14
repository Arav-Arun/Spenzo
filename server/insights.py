"""Answers you can see: spending charts and the monthly Wrapped card, sent as pictures in chat."""
import calendar
from collections import Counter
from datetime import date
from typing import Literal

from server import cards, db
from server.core import check_date, current_user, month_range, today
from server.replies import Reply, inr

MIN_WRAPPED = 5   # spends needed for a Wrapped worth sharing


def _months_back(day: date, n: int) -> date:
    y, m = divmod(day.year * 12 + day.month - 1 - n, 12)
    return date(y, m + 1, 1)


def _match(search: str) -> tuple[str, list]:
    term = search.strip().lower()
    if not term.strip("*%_ "):
        return "", []
    like = "%" + term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    return (" and (description ilike %s or note ilike %s or category ilike %s or %s = any(tags))",
            [like, like, like, term])


def _expenses(start: str, end: str, search: str = "") -> list[dict]:
    where, params = _match(search)
    return db.rows(f"select date, amount, category, description from transactions where phone = %s "
                   f"and kind = 'expense' and date between %s and %s{where}", current_user(), start, end, *params)


def _range_label(start: str, end: str) -> str:
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if (a.year, a.month) == (b.year, b.month):
        return a.strftime("%B %Y")
    return f"{a.strftime('%b %Y')} – {b.strftime('%b %Y')}" if a.year != b.year else f"{a.strftime('%b')} – {b.strftime('%b %Y')}"


def spending_chart(group_by: Literal["category", "merchant", "month", "day"] = "category",
                   start_date: str = "", end_date: str = "", search: str = "",
                   compare_previous_year: bool = False) -> dict:
    """Draw the user's spending as a picture: by category, by merchant, by month or by day.
    search keeps only matching spends ("swiggy", "Food & Dining", a tag). Dates are YYYY-MM-DD;
    leave them empty for this month, or for group_by='month' the last 6 months. For "this year vs
    last", use group_by='month' with compare_previous_year=True (this year so far against the same
    months last year). The picture is attached to your reply automatically."""
    now = date.fromisoformat(today())
    if start_date and end_date:
        start, end = check_date(start_date, future_days=366, past_days=1500), check_date(end_date, future_days=366)
    elif group_by == "month":
        start = (date(now.year, 1, 1) if compare_previous_year else _months_back(now, 5)).isoformat()
        end = month_range()[1]
    else:
        start, end = month_range()
    rows = _expenses(start, end, search)
    if not rows and not compare_previous_year:
        raise ValueError(f"No spending{f' matching {search!r}' if search else ''} between {start} and {end}.")
    what = search.strip().title() or "Spending"
    total = sum(r["amount"] for r in rows)
    result = {"from": start, "to": end, "search": search, "total": round(total, 2)}

    if group_by in ("category", "merchant"):
        key = (lambda r: r["category"]) if group_by == "category" else \
            (lambda r: (r["description"] or r["category"]).strip().title())
        totals = Counter()
        for r in rows:
            totals[key(r)] += r["amount"]
        top = [(k, round(v, 2)) for k, v in totals.most_common(8)]
        result["rows"] = [{"name": k, "total": v} for k, v in top]
        title = f"{what} by {'category' if group_by == 'category' else 'place'}"
        result["_image"] = cards.bars(title, _range_label(start, end), inr(round(total)), top)
        return result

    if group_by == "month":
        a, b = date.fromisoformat(start), date.fromisoformat(end)
        months = [_months_back(b, i) for i in range((b.year - a.year) * 12 + b.month - a.month, -1, -1)]
        sums = Counter()
        for r in rows:
            sums[r["date"][:7]] += r["amount"]
        this = [round(sums[m.strftime("%Y-%m")], 2) for m in months]
        labels = [m.strftime("%b") for m in months]
        series = [(str(a.year), this, cards.LEAF)]
        result["by_month"] = dict(zip([m.strftime("%Y-%m") for m in months], this, strict=True))
        subtitle = _range_label(start, end)
        if compare_previous_year:
            last_rows = _expenses(date(a.year - 1, a.month, 1).isoformat(),
                                  date(b.year - 1, b.month, calendar.monthrange(b.year - 1, b.month)[1]).isoformat(),
                                  search)
            last = Counter()
            for r in last_rows:
                last[r["date"][:7]] += r["amount"]
            before = [round(last[f"{m.year - 1}-{m.month:02d}"], 2) for m in months]
            if not rows and not last_rows:
                raise ValueError(f"No spending{f' matching {search!r}' if search else ''} this year or last.")
            series = [(str(a.year - 1), before, cards.MANGO), (str(a.year), this, cards.LEAF)]
            result["previous_year_total"] = round(sum(before), 2)
            result["previous_year_by_month"] = dict(zip([f"{m.year - 1}-{m.month:02d}" for m in months], before, strict=True))
            subtitle = f"{labels[0]}–{labels[-1]}, {a.year} vs {a.year - 1}"
        result["_image"] = cards.columns(f"{what} by month", subtitle, inr(round(total)), labels, series)
        return result

    a, b = date.fromisoformat(start), date.fromisoformat(end)
    days = [date.fromordinal(o) for o in range(a.toordinal(), min(b, max(now, a)).toordinal() + 1)][:62]
    sums = Counter()
    for r in rows:
        sums[r["date"]] += r["amount"]
    values = [round(sums[d.isoformat()], 2) for d in days]
    result["by_day"] = {d.isoformat(): v for d, v in zip(days, values, strict=True) if v}
    result["_image"] = cards.columns(f"{what} by day", _range_label(start, end), inr(round(total)),
                                     [str(d.day) for d in days], [("", values, cards.LEAF)])
    return result


# --- Wrapped ---------------------------------------------------------------------------


def _change(now: float, before: float) -> str:
    if not before:
        return ""
    pct = round(100 * (now / before - 1))
    return f"{abs(pct)}% {'more' if pct > 0 else 'less'} than last month" if pct else "same as last month"


def wrapped(month: str = "") -> dict:
    """The user's month as one shareable picture: total, top category and place, their most
    repeated spend, busiest day and no-spend days. month is YYYY-MM; leave it empty for last month
    (or this month so far if last month is nearly empty). The picture is attached automatically."""
    now = date.fromisoformat(today())
    if month:
        first = date.fromisoformat(f"{month}-01")
    else:
        first = _months_back(now, 1)
        if len(_expenses(*month_range(first.isoformat()))) < MIN_WRAPPED:
            first = now.replace(day=1)
    start, end = month_range(first.isoformat())
    rows = _expenses(start, end)
    name = first.strftime("%B %Y")
    if len(rows) < MIN_WRAPPED:
        raise ValueError(f"Only {len(rows)} spends in {name}, not enough for a Wrapped yet.")

    total = sum(r["amount"] for r in rows)
    before = sum(r["amount"] for r in _expenses(*month_range(_months_back(first, 1).isoformat())))
    by_cat, by_place, counts, by_weekday = Counter(), Counter(), Counter(), Counter()
    for r in rows:
        by_cat[r["category"]] += r["amount"]
        label = (r["description"] or "").strip().title()
        if label:
            by_place[label] += r["amount"]
            counts[label] += 1
        by_weekday[date.fromisoformat(r["date"]).strftime("%A")] += r["amount"]
    last_day = min(date.fromisoformat(end), now)
    no_spend = (last_day - first).days + 1 - len({r["date"] for r in rows})
    cat, cat_total = by_cat.most_common(1)[0]
    biggest = max(rows, key=lambda r: r["amount"])

    income = db.value("select coalesce(sum(amount), 0) from transactions where phone = %s and kind = 'income' "
                      "and date between %s and %s", current_user(), start, end)
    tiles = [("Top category", cat, f"{round(100 * cat_total / total)}% · {inr(round(cat_total))}")]
    if by_place:
        # The place you went back to most; by money if nowhere was visited twice.
        place = max(by_place, key=lambda p: (counts[p] >= 2, counts[p] if counts[p] >= 2 else 0, by_place[p]))
        visits = "once" if counts[place] == 1 else f"{counts[place]} times"
        tiles.append(("Top spot", place, f"{inr(round(by_place[place]))} · {visits}"))
    usual, times = counts.most_common(1)[0] if counts else ("", 0)
    if times >= 3:
        tiles.append(("Your usual", f"{times} × {usual}", f"{inr(round(by_place[usual]))} in all"))
    tiles.append(("Biggest day", by_weekday.most_common(1)[0][0], "you spend most on these"))
    tiles.append(("Biggest spend", inr(biggest["amount"]), (biggest["description"] or biggest["category"]).title()))
    tiles.append(("No-spend days", str(max(no_spend, 0)), "days you spent nothing"))
    if income > total:
        tiles.append(("Money left", inr(round(income - total)), f"of {inr(round(income))} that came in"))

    line = f"spent across {len(rows)} spends"
    change = _change(total, before)
    if change:
        line += f", {change}"
    stats = {"month": name, "total": round(total, 2), "spends": len(rows), "vs_last_month": change,
             "tiles": [{"label": a, "value": b, "detail": c} for a, b, c in tiles]}
    return stats | {"_image": cards.wrapped(name, inr(round(total)), line, tiles)}


def wrapped_reply(month: str = "") -> Reply:
    """The Wrapped card with a short caption (no AI needed)."""
    try:
        w = wrapped(month)
    except ValueError as e:
        return Reply(f"{e} Keep logging and ask me again 🙂")
    return Reply(f"🎁 *Your {w['month'].split()[0]} Wrapped*\n{inr(round(w['total']))} across {w['spends']} spends. "
                 "Forward it to a friend who needs a money buddy 😉", png=w["_image"])
