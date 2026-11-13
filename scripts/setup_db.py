"""Create Spenzo's tables. Safe to run again.

Uses the direct connection (DATABASE_URL_UNPOOLED) when there is one, as Neon recommends for
schema changes, and falls back to DATABASE_URL.

    uv run python scripts/setup_db.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg  # noqa: E402

from server.core import env  # noqa: E402  (loads .env)

url = env("DATABASE_URL_UNPOOLED") or env("DATABASE_URL")
if not url:
    sys.exit("Set DATABASE_URL in .env first.")
with psycopg.connect(url, autocommit=True) as conn:
    conn.execute((ROOT / "schema.sql").read_text())
    tables = [r[0] for r in conn.execute(
        "select table_name from information_schema.tables where table_schema = 'public' order by 1").fetchall()]
print("Ready. Tables:", ", ".join(tables))
