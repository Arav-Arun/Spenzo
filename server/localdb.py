"""A throwaway Postgres on your machine, for tests and `server.chat --memory`. Needs the dev extras."""
import tempfile
from contextlib import contextmanager
from pathlib import Path

import psycopg

from server import db

SCHEMA = Path(__file__).resolve().parent.parent / "schema.sql"


@contextmanager
def throwaway_database():
    import pgserver   # dev dependency: an embedded Postgres, no install needed

    with tempfile.TemporaryDirectory(prefix="spenzo-pg-") as folder:
        server = pgserver.get_server(folder, cleanup_mode="stop")
        try:
            url = server.get_uri()
            with psycopg.connect(url, autocommit=True) as conn:
                conn.execute(SCHEMA.read_text())
            db.use_url(url)
            yield url
        finally:
            db.close()
            db.use_url(None)
            server.cleanup()
