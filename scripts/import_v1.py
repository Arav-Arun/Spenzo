"""Copy the old Spenzo (v1, Supabase) ledger into the v2 database. Run once at launch.

    V1_SUPABASE_URL=... V1_SUPABASE_KEY=... uv run python scripts/import_v1.py          # dry run
    V1_SUPABASE_URL=... V1_SUPABASE_KEY=... uv run python scripts/import_v1.py --apply

Reads v1's `expenses` table over Supabase's REST API (read-only) and writes to DATABASE_URL.
Rows in v1's "Receivable" category become debts; everything else becomes an expense.
Safe to re-run: it refuses to import if v2 already has transactions.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from server import db  # noqa: E402


def phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    return f"+{digits}" if digits else (raw or "local")


def fetch_v1() -> list[dict]:
    url, key = os.environ["V1_SUPABASE_URL"].rstrip("/"), os.environ["V1_SUPABASE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    out, start = [], 0
    with httpx.Client(timeout=30) as client:
        while True:
            page = client.get(f"{url}/rest/v1/expenses", params={"select": "*", "order": "id"},
                              headers=headers | {"Range": f"{start}-{start + 999}"}).raise_for_status().json()
            out += page
            if len(page) < 1000:
                return out
            start += 1000


def main(apply: bool) -> None:
    rows = fetch_v1()
    expenses = [r for r in rows if r.get("category") != "Receivable"]
    debts = [r for r in rows if r.get("category") == "Receivable"]
    users = {phone(r.get("phone_number")) for r in rows}
    print(f"v1 has {len(expenses)} expenses and {len(debts)} IOUs from {len(users)} users.")
    if not apply:
        print("Dry run. Re-run with --apply to copy them into DATABASE_URL.")
        return
    if db.value("select count(*) from transactions"):
        sys.exit("v2 already has transactions; refusing to import twice.")
    with db.transaction():
        for u in users:
            db.execute("insert into users (phone) values (%s) on conflict do nothing", u)
        for r in expenses:
            db.execute("insert into transactions (phone, date, kind, amount, category, description, note) "
                       "values (%s, %s, 'expense', %s, %s, %s, %s)", phone(r.get("phone_number")), r["date"],
                       r["amount"], r["category"], r.get("subcategory") or "", r.get("note") or "")
        for r in debts:
            db.execute("insert into debts (phone, person, direction, amount, reason, date) "
                       "values (%s, %s, 'they_owe', %s, %s, %s)", phone(r.get("phone_number")),
                       r.get("subcategory") or "Someone", r["amount"], r.get("note") or "", r["date"])
    print("Imported.")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
