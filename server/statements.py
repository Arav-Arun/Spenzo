"""Forwarded PDFs: a bank or card statement fills in a whole month at once, a mutual fund or
demat statement (CAS) fills in the portfolio, and a receipt is logged like a photo of a bill.

The PDF's text goes to the model, which returns every row as JSON. Rows already logged by hand
(same day, kind and amount) are skipped, and so are transfers between the user's own accounts,
card bill payments and reversals. Each import gets an id, so one tap undoes it.

Locked PDFs (most Indian statements are) wait up to 10 minutes for the password. The password
never reaches the AI or the chat history, and is forgotten once the PDF opens.
"""
import io
import json
import logging
import secrets
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from openai import OpenAI
from pypdf import PdfReader

from server import db, save
from server.core import check_date, current_user, env
from server.replies import Reply, inr, logged
from server.spend import CATEGORIES, FIELDS

log = logging.getLogger("spenzo")

MODEL = env("OPENAI_MODEL", "gpt-4.1-mini")
MAX_PAGES, CHUNK_CHARS, LOCK_SECONDS = 40, 12_000, 600
INCOME = ["Salary", "Freelance", "Refund", "Interest", "Gift", "Other income"]
SKIP_REASONS = {"own_transfer": ("transfer", "between your own accounts"), "card_payment": ("card bill payment", ""),
                "investment": ("investment", "(SIPs, stock buys)"), "reversal": ("reversed or failed payment", "")}

_locked: dict[str, tuple[float, bytes, str]] = {}   # phone → (when, pdf, file name)

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["kind", "institution", "transactions", "holdings"],
    "properties": {
        "kind": {"type": "string", "enum": ["bank_statement", "card_statement", "investment_statement", "receipt", "other"]},
        "institution": {"type": "string"},
        "transactions": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["date", "amount", "direction", "description", "category", "skip"],
            "properties": {
                "date": {"type": "string"}, "amount": {"type": "number"},
                "direction": {"type": "string", "enum": ["debit", "credit"]},
                "description": {"type": "string"},
                "category": {"type": "string", "enum": [*CATEGORIES, *INCOME]},
                "skip": {"type": "string", "enum": ["no", *SKIP_REASONS]},
            }}},
        "holdings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["name", "kind", "units", "invested"],
            "properties": {
                "name": {"type": "string"}, "kind": {"type": "string", "enum": ["stock", "mutual_fund"]},
                "units": {"type": "number"}, "invested": {"type": "number"},
            }}},
    },
}

PROMPT = """You read Indian financial documents and return their rows as JSON.
kind: bank_statement, card_statement (credit card), investment_statement (mutual fund or demat
CAS, a broker holdings statement), receipt (one purchase: invoice, bill, order) or other.
institution: the bank, card, AMC or shop, short ("HDFC Bank", "CAMS", "Amazon").

transactions: every money movement, using the document's own dates as YYYY-MM-DD and amounts in
rupees. debit = money out of the user's account or onto their card; credit = money in. For a
receipt, one debit for the total. description: a short clean name of the merchant or person
("UPI/ZOMATO/1234/..." -> "Zomato", "NEFT-ACME PVT LTD-SALARY" -> "Acme salary"). category:
for debits pick from {expense}; for credits from {income}. skip: own_transfer for moves between
the user's own accounts or wallets, card_payment for paying a credit card bill, investment for
SIPs, mutual fund or stock purchases, reversal for failed, reversed or refunded-the-same-day
pairs (mark both sides); otherwise no.

holdings: for an investment statement, every fund or stock with units (or shares) and the amount
invested (cost value; 0 if not shown). Otherwise an empty list.
Never invent rows. If the text is cut off, return the rows you can read."""


def _client() -> OpenAI:
    return OpenAI()


# --- Reading ----------------------------------------------------------------------


class Locked(Exception):
    pass


def text_of(data: bytes, password: str = "") -> str:
    """The PDF's text, page by page. Raises Locked if it needs a (different) password."""
    reader = PdfReader(io.BytesIO(data))
    if reader.is_encrypted and not reader.decrypt(password):
        raise Locked()
    return "\n\n".join(page.extract_text() or "" for page in reader.pages[:MAX_PAGES]).strip()


def _chunks(text: str) -> list[str]:
    out, current = [], ""
    for line in text.splitlines():
        if len(current) + len(line) > CHUNK_CHARS and current:
            out.append(current)
            current = ""
        current += line + "\n"
    return out + [current] if current.strip() else out


def _extract(chunk: str, part: int, parts: int) -> dict:
    note = f"\n\n(This is part {part} of {parts} of the document.)" if parts > 1 else ""
    resp = _client().chat.completions.create(
        model=MODEL, temperature=0, max_tokens=16_000,
        response_format={"type": "json_schema", "json_schema": {"name": "document", "strict": True, "schema": SCHEMA}},
        messages=[{"role": "system", "content": PROMPT.format(expense=", ".join(CATEGORIES), income=", ".join(INCOME))},
                  {"role": "user", "content": chunk + note}])
    return json.loads(resp.choices[0].message.content)


def extract(text: str) -> dict:
    """Every row in the document, read in parallel chunks for long statements."""
    chunks = _chunks(text)
    with ThreadPoolExecutor(max_workers=4) as pool:
        parts = list(pool.map(lambda ic: _extract(ic[1], ic[0] + 1, len(chunks)), enumerate(chunks)))
    first = parts[0]
    return {"kind": first["kind"], "institution": first["institution"],
            "transactions": [t for p in parts for t in p["transactions"]],
            "holdings": [h for p in parts for h in p["holdings"]]}


# --- Saving -----------------------------------------------------------------------


def save_transactions(rows: list[dict], source: str) -> dict:
    """Insert statement rows, skipping ones the user already logged and non-spending moves."""
    keep, skipped, bad = [], Counter(), 0
    for t in rows:
        try:
            check_date(t["date"], past_days=1100)
        except ValueError:
            bad += 1
            continue
        if t["amount"] <= 0:
            bad += 1
        elif t["skip"] != "no":
            skipped[t["skip"]] += 1
        else:
            keep.append(t)
    if not keep:
        return {"added": [], "already_had": 0, "skipped": dict(skipped), "unreadable": bad}

    dates = sorted(t["date"] for t in keep)
    existing = Counter((r["kind"], r["date"], round(r["amount"], 2)) for r in db.rows(
        "select kind, date, amount from transactions where phone = %s and date between %s and %s",
        current_user(), dates[0], dates[-1]))
    added, already = [], 0
    with db.transaction():
        for t in keep:
            kind = "expense" if t["direction"] == "debit" else "income"
            key = (kind, t["date"], round(t["amount"], 2))
            if existing[key]:
                existing[key] -= 1
                already += 1
                continue
            category = t["category"] if (kind == "expense") == (t["category"] in CATEGORIES) else \
                ("Other" if kind == "expense" else "Other income")
            added.append(db.row(
                f"insert into transactions (phone, date, kind, amount, category, description, source) "
                f"values (%s, %s, %s, %s, %s, %s, %s) returning {FIELDS}",
                current_user(), t["date"], kind, round(t["amount"], 2), category, t["description"].strip()[:80], source))
    return {"added": added, "already_had": already, "skipped": dict(skipped), "unreadable": bad}


def save_holdings(rows: list[dict]) -> dict:
    added, failed = [], []
    for h in rows:
        if h["units"] <= 0:
            continue
        try:
            avg = h["invested"] / h["units"] if h["invested"] else 0
            added.append(save.add_investment(h["name"], h["units"], avg, kind=h["kind"])["added"])
        except Exception as e:   # one unknown fund shouldn't sink the rest
            log.warning("holding %s not added: %s", h["name"], e)
            failed.append(h["name"])
    return {"added": added, "failed": failed}


# --- Replies ----------------------------------------------------------------------


def _period(rows: list[dict]) -> str:
    days = sorted(date.fromisoformat(r["date"]) for r in rows)
    first, last = days[0], days[-1]
    return first.strftime("%-d %b") + (f" – {last.strftime('%-d %b')}" if last != first else "")


def _n(count: int, one: str, many: str = "") -> str:
    """3 spends, 1 spend."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


def summary(doc: dict, filename: str) -> Reply:
    kind, name = doc["kind"], doc["institution"] or filename or "your document"
    if kind == "investment_statement" and doc["holdings"]:
        result = save_holdings(doc["holdings"])
        if not result["added"]:
            return Reply("I found holdings in that statement but couldn't match them to live prices. "
                         "Try sending a screenshot of your holdings instead.")
        lines = [f"📈 *{name}*: added {len(result['added'])} holdings to your portfolio."]
        if result["failed"]:
            lines.append(f"Couldn't price: {', '.join(result['failed'][:3])}.")
        lines.append("Ask *how are my investments doing?* to see them at today's prices.")
        return Reply("\n".join(lines))

    if not doc["transactions"]:
        return Reply("I couldn't find any transactions in that PDF. If it's a scan, send screenshots of the pages instead.")

    if kind == "receipt" and len(doc["transactions"]) == 1:
        result = save_transactions(doc["transactions"], source=None)
        if result["added"]:
            return logged(result["added"][0])
        return Reply("Looks like you already logged that one 👍")

    batch = "stmt:" + secrets.token_hex(4)
    result = save_transactions(doc["transactions"], source=batch)
    added = result["added"]
    spent = [t for t in added if t["kind"] == "expense"]
    income = [t for t in added if t["kind"] == "income"]
    lines = [f"📄 *{name}* · {_period(doc['transactions'])}"]
    if added:
        parts = [f"{_n(len(spent), 'spend')} ({inr(round(sum(t['amount'] for t in spent)))})"] if spent else []
        parts += [f"{_n(len(income), 'credit')} ({inr(round(sum(t['amount'] for t in income)))})"] if income else []
        lines.append("Added " + " and ".join(parts) + ".")
    left_out = [f"{result['already_had']} you'd already logged"] if result["already_had"] else []
    left_out += [" ".join(filter(None, [_n(n, SKIP_REASONS[r][0]), SKIP_REASONS[r][1]]))
                 for r, n in result["skipped"].items()]
    if left_out:
        lines.append("Left out " + ", ".join(left_out) + ".")
    if spent:
        big = max(spent, key=lambda t: t["amount"])
        lines.append(f"Biggest: {big['description'] or big['category']} {inr(round(big['amount']))}.")
    if not added:
        return Reply("\n".join(lines + ["Nothing new to add: it's all logged already 👍"]))
    return Reply("\n".join(lines), buttons=[("month", "📊 This month"), (f"undo_import:{batch}", "↩️ Undo import")])


def _read_and_save(data: bytes, filename: str, password: str = "") -> Reply:
    text = text_of(data, password)
    if len(text) < 40:
        return Reply("That PDF looks like a scan, so I can't read its text. Send screenshots of the pages instead.")
    return summary(extract(text), filename)


def from_pdf(data: bytes, filename: str = "") -> Reply:
    """A PDF sent or forwarded to Spenzo."""
    _locked.pop(current_user(), None)
    try:
        return _read_and_save(data, filename)
    except Locked:
        _locked[current_user()] = (time.time(), data, filename)
        return Reply("🔒 That PDF is locked. Send me its password and I'll open it.\n"
                     "_Bank statements usually use a mix of your name, date of birth or customer ID; the "
                     "email they came with says which. I don't keep the password._")
    except Exception:
        log.exception("Couldn't read a PDF")
        return Reply("I couldn't read that PDF. Is it a bank, card or mutual fund statement, or a bill?")


def waiting_for_password() -> bool:
    hit = _locked.get(current_user())
    if hit and time.time() - hit[0] > LOCK_SECONDS:
        _locked.pop(current_user(), None)
        return False
    return hit is not None


def with_password(password: str) -> Reply:
    if password.lower() in ("cancel", "skip", "stop", "no"):
        _locked.pop(current_user(), None)
        return Reply("Okay, skipped that PDF.")
    _, data, filename = _locked[current_user()]
    try:
        reply = _read_and_save(data, filename, password)
    except Locked:
        return Reply("That password didn't open it. Try again, or send *cancel*.")
    except Exception:
        log.exception("Couldn't read a PDF")
        reply = Reply("It opened, but I couldn't read it. Try screenshots of the pages instead.")
    _locked.pop(current_user(), None)
    return reply
