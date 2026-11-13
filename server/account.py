"""Link Claude Desktop to a WhatsApp number so both share one ledger.

Claude shows a 6-digit code; the user sends "link <code>" to Spenzo on WhatsApp.
That proves they own the number, and costs nothing (no outbound OTP message).
"""
import os
import secrets
from datetime import datetime, timedelta, timezone

from server import db
from server.core import LINK_FILE, current_user

CODE_MINUTES = 10


def link_whatsapp() -> dict:
    """Start linking this Claude Desktop to the user's Spenzo WhatsApp chat."""
    code = f"{secrets.randbelow(10**6):06d}"
    expires = (datetime.now(timezone.utc) + timedelta(minutes=CODE_MINUTES)).isoformat()
    db.execute("insert into link_codes (code, expires_at) values (%s, %s)", code, expires)
    return {"code": code, "next": f"Ask the user to send 'link {code}' to Spenzo on WhatsApp, "
                                  f"then call finish_linking with the code. It expires in {CODE_MINUTES} minutes."}


def finish_linking(code: str) -> dict:
    """Complete linking after the user has sent 'link <code>' on WhatsApp."""
    found = db.row("select phone from link_codes where code = %s and expires_at > now()", code.strip())
    if not found:
        raise ValueError("That code is unknown or expired. Start again with link_whatsapp.")
    if not found["phone"]:
        raise ValueError("Spenzo hasn't received the code on WhatsApp yet. Ask the user to send it, then try again.")
    phone = found["phone"]
    db.execute("delete from link_codes where code = %s", code.strip())
    LINK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LINK_FILE.write_text(phone)
    os.environ["LINKED_PHONE"] = phone
    return {"status": "linked", "phone": phone, "message": "Claude and WhatsApp now share one ledger."}


def claim_code(code: str) -> bool:
    """WhatsApp side: the sender (current user) claims a code shown in Claude."""
    return db.execute("update link_codes set phone = %s where code = %s and phone is null and expires_at > now()",
                      current_user(), code) == 1
