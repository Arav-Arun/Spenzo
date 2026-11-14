"""Sign-in with no passwords: WhatsApp is the account.

Spenzo sends a one-tap link in chat. The link carries a short-lived signed token
(15 minutes) that the dashboard swaps for a 30-day session token. Bumping the user's
session_version signs out every browser at once.
"""
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time

from server import brand, db
from server.core import current_user, env

MAGIC_SECONDS = 15 * 60
SESSION_SECONDS = 30 * 24 * 3600

_secret = env("SECRET_KEY").encode() or secrets.token_bytes(32)
if not env("SECRET_KEY"):
    logging.getLogger("spenzo").warning("SECRET_KEY not set: dashboard links will stop working on restart.")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _version(phone: str) -> int:
    return db.value("select session_version from users where phone = %s", phone) or 0


def make_token(phone: str, purpose: str, seconds: int) -> str:
    body = _b64(json.dumps({"p": phone, "u": purpose, "e": int(time.time()) + seconds, "v": _version(phone)}).encode())
    sig = _b64(hmac.new(_secret, body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def read_token(token: str, purpose: str) -> str:
    """The phone number a valid token belongs to, or ValueError."""
    try:
        body, sig = token.split(".")
        good = _b64(hmac.new(_secret, body.encode(), hashlib.sha256).digest())
        data = json.loads(_unb64(body))
    except Exception:
        raise ValueError("Invalid link.")
    if not hmac.compare_digest(sig, good) or data.get("u") != purpose:
        raise ValueError("Invalid link.")
    if data["e"] < time.time():
        raise ValueError("This link has expired. Ask Spenzo for a new one.")
    if data["v"] != _version(data["p"]):
        raise ValueError("You were signed out. Ask Spenzo for a new link.")
    return data["p"]


def dashboard_url() -> str:
    # The token rides in the #fragment, so it never reaches server logs or other sites.
    return f"{brand.WEB_URL}/app#t={make_token(current_user(), 'magic', MAGIC_SECONDS)}"


def dashboard_link() -> dict:
    """A one-tap link to the user's dashboard (charts, budgets, goals, friends, investments).
    It's attached as a button automatically; don't paste the URL."""
    return {"_link": ("📊 Open dashboard", dashboard_url()), "valid_for_minutes": MAGIC_SECONDS // 60}

