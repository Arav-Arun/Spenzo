"""Postgres, in plain SQL. Works with Neon, Supabase or any Postgres via DATABASE_URL.

    rows("select ... where phone = %s", phone)   -> list[dict]
    row(...)                                     -> dict | None
    value(...)                                   -> first column of the first row
    execute(...)                                 -> rows affected
    with transaction(): ...                      -> several statements, all or nothing

Numbers come back as float and dates as 'YYYY-MM-DD' strings, so the rest of the
code (and the JSON it returns) never deals with Decimal or date objects.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg.types.numeric import FloatLoader
from psycopg.types.string import TextLoader
from psycopg_pool import ConnectionPool

from server.core import env

__all__ = ["Jsonb", "execute", "row", "rows", "transaction", "use_url", "value"]

_url_override: str | None = None
_in_transaction: ContextVar[Connection | None] = ContextVar("spenzo_tx", default=None)


def _configure(conn: Connection) -> None:
    conn.adapters.register_loader("numeric", FloatLoader)
    conn.adapters.register_loader("date", TextLoader)


@lru_cache
def _pool(url: str) -> ConnectionPool:
    # prepare_threshold=None: Neon's and Supabase's poolers don't support prepared statements.
    # Neon's free tier suspends an idle database and closes its connections, so test each
    # connection before handing it out (check) and retire idle ones before Neon does (max_idle).
    return ConnectionPool(url, min_size=1, max_size=5, open=True, configure=_configure,
                          check=ConnectionPool.check_connection, max_idle=120,
                          kwargs={"autocommit": True, "row_factory": dict_row, "prepare_threshold": None})


def _url() -> str:
    url = _url_override or env("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Put your Neon (or any Postgres) connection string in .env.")
    return url


def use_url(url: str | None) -> None:
    """Point Spenzo at another database (tests and the local simulator)."""
    global _url_override
    _url_override = url


@contextmanager
def _connection():
    conn = _in_transaction.get()
    if conn is not None:
        yield conn
        return
    with _pool(_url()).connection() as conn:
        yield conn


@contextmanager
def transaction():
    if _in_transaction.get() is not None:   # already inside one
        yield
        return
    with _pool(_url()).connection() as conn, conn.transaction():
        token = _in_transaction.set(conn)
        try:
            yield
        finally:
            _in_transaction.reset(token)


def rows(sql: str, *params) -> list[dict]:
    with _connection() as conn:
        cur = conn.execute(sql, params or None)   # no params: a literal % in the SQL stays literal
        return cur.fetchall() if cur.description else []


def row(sql: str, *params) -> dict | None:
    found = rows(sql, *params)
    return found[0] if found else None


def value(sql: str, *params):
    found = row(sql, *params)
    return next(iter(found.values())) if found else None


def execute(sql: str, *params) -> int:
    with _connection() as conn:
        return conn.execute(sql, params or None).rowcount


def close() -> None:
    for pool in [_pool(u) for u in {_url_override, env("DATABASE_URL")} if u]:
        pool.close()
    _pool.cache_clear()
