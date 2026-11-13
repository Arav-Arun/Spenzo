"""Dashboard API. Every call needs a session from POST /api/session (see auth.py)."""
import csv
import io
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from server import auth, core, db, profile, save, spend, split
from server.core import month_range

router = APIRouter(prefix="/api")


class SessionRequest(BaseModel):
    token: str


def _signed_in(request: Request) -> None:
    header = request.headers.get("authorization", "")
    try:
        core.set_user(auth.read_token(header.removeprefix("Bearer ").strip(), "session"))
    except ValueError as e:
        raise HTTPException(401, str(e))


def _month(month: str) -> tuple[str, str]:
    try:
        return month_range(f"{month}-01") if month else month_range()
    except ValueError:
        raise HTTPException(400, "month must look like 2026-11")


@router.post("/session")
def start_session(body: SessionRequest):
    """Swap the 15-minute link token for a 30-day session."""
    try:
        phone = auth.read_token(body.token, "magic")
    except ValueError as e:
        raise HTTPException(401, str(e))
    core.set_user(phone)
    user = profile.get() or {}
    return {"session": auth.make_token(phone, "session", auth.SESSION_SECONDS), "name": user.get("name", "")}


@router.get("/overview")
def overview(request: Request, month: str = ""):
    _signed_in(request)
    start, end = _month(month)
    rows = spend.list_transactions(start, end, kind="expense")
    days: dict[str, float] = {}
    for r in rows:
        days[r["date"]] = days.get(r["date"], 0) + r["amount"]
    d, last = date.fromisoformat(start), date.fromisoformat(end)
    daily = []
    while d <= last:
        daily.append({"date": d.isoformat(), "spent": round(days.get(d.isoformat(), 0), 2)})
        d += timedelta(days=1)
    user = profile.get() or {}
    return {
        "name": user.get("name", ""), "month": start[:7],
        "summary": spend.summarize(start, end), "daily": daily,
        "budgets": spend.budget_status() if start == month_range()[0] else [],
        "goals": save.goals_status(), "debts": split.list_debts(),
        "recent": sorted(rows + spend.list_transactions(start, end, kind="income"),
                         key=lambda r: (r["date"], r["id"]), reverse=True)[:50],
    }


@router.get("/portfolio")
def portfolio(request: Request):
    _signed_in(request)
    return save.portfolio()


@router.delete("/transactions/{transaction_id}")
def delete(request: Request, transaction_id: int):
    _signed_in(request)
    try:
        return spend.delete_transaction(transaction_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/export.csv")
def export(request: Request):
    _signed_in(request)
    rows = db.rows(f"select {spend.FIELDS} from transactions where phone = %s order by date, id", core.current_user())
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "kind", "amount", "category", "description", "note", "tags"])
    for r in rows:
        writer.writerow([r["date"], r["kind"], r["amount"], r["category"], r["description"], r["note"], " ".join(r["tags"] or [])])
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=spenzo.csv"})
