"""Test Spenzo on real WhatsApp, end to end. Replies arrive on your phone.

    ./scripts/dev.sh                        # bot + tunnel running, webhook connected
    # from your phone, send "hi" to the test number first (WhatsApp only lets a business
    # reply within 24 hours of your last message)
    uv run python scripts/whatsapp_test.py  # --keep keeps the test data; --phone +91… picks the tester

1. Webhook path: posts one message to the bot exactly as Meta does (signed with your app
   secret) and checks it was saved to the database.
2. Conversation: runs a scripted chat as you, and sends every reply to your phone through
   the WhatsApp Cloud API, checking each one is accepted.
3. Cleans up: deletes everything the test created (unless --keep).
"""
import asyncio
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx  # noqa: E402

from server import core, db, profile, whatsapp  # noqa: E402
from server.conversation import Incoming, respond  # noqa: E402

BOT = core.env("BOT_URL", "http://localhost:8000")
# Each step, and what must be true in the database (or the reply) afterwards.
SCRIPT = [
    ("uber 260", "select count(*) from transactions where phone = %s and description ilike '%%uber%%'"),
    ("[tap 1]", "select count(*) = 0 from transactions where phone = %s and description ilike '%%uber%%'"),
    ("dinner 3000 split with Arav and Riya", "select count(*) = 2 from debts where phone = %s"),
    ("keep food under 1500", "select count(*) from budgets where phone = %s and category = 'Food & Dining'"),
    ("swiggy 400", "reply: % of ₹1,500"),
    ("Goa trip 30k by March", "select count(*) from goals where phone = %s"),
    ("salary 60k", "select count(*) from transactions where phone = %s and kind = 'income'"),
    ("[tap 1]", "select max(saved) = 7500 from goals where phone = %s"),
    ("who owes me?", "reply: Riya"),
    ("Arav paid me back", "select count(*) = 0 from debts where phone = %s and lower(person) = 'arav'"),
    ("I have 10 TCS shares bought at 2200", "select count(*) from holdings where phone = %s"),
    ("how are my investments doing?", "reply: ₹"),
    ("kitna kharcha hua is mahine?", "reply: ₹"),
    ("[month]", "reply: so far"),
    ("login", "reply: dashboard"),
    ("connect ai", "reply: link"),
]


def tester() -> str:
    if "--phone" in sys.argv:
        return core.phone(sys.argv[sys.argv.index("--phone") + 1])
    phone = db.value("select phone from users where phone like '+%' order by created_at desc limit 1")
    if not phone:
        sys.exit("No one has messaged the bot yet. Send 'hi' to the test number from your phone, then rerun.")
    return phone


async def webhook_check(phone: str) -> bool:
    body = json.dumps({"entry": [{"changes": [{"value": {
        "contacts": [{"wa_id": phone.lstrip("+"), "profile": {"name": "Test"}}],
        "messages": [{"id": f"wamid.test.{time.time()}", "from": phone.lstrip("+"), "type": "text",
                      "text": {"body": "chai 20 (webhook test)"}}]}}]}]}).encode()
    sig = "sha256=" + hmac.new(core.env("WHATSAPP_APP_SECRET").encode(), body, hashlib.sha256).hexdigest()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BOT}/webhook", content=body, headers={"X-Hub-Signature-256": sig})
    if resp.status_code != 200:
        print(f"  ✗ webhook answered {resp.status_code} (is ./scripts/dev.sh running?)")
        return False
    for _ in range(30):   # the bot answers in the background
        if db.value("select count(*) from transactions where phone = %s and description ilike %s", phone, "%chai%"):
            print("  ✓ signed webhook accepted, message understood and saved; reply sent to your phone")
            return True
        await asyncio.sleep(1)
    print("  ✗ webhook accepted but nothing was saved within 30s (check the dev.sh terminal)")
    return False


async def conversation(phone: str) -> int:
    failures, buttons = 0, []
    for line, check in SCRIPT:
        msg = Incoming(phone=phone, name="Test")
        if line.startswith("[tap"):
            msg.button_id = buttons[int(line[5]) - 1] if buttons else ""
        elif line == "[month]":
            msg.button_id = "month"
        else:
            msg.text = line
        label = line if not msg.button_id else f"[tap {msg.button_id.split(':')[0]}]"
        replies = await respond(msg)
        delivered = [await whatsapp.send(phone, r) for r in replies]
        text = "\n".join(r.text for r in replies) + " " + " ".join(r.link[0] for r in replies if r.link)
        if check.startswith("reply: "):
            saved = check[7:].lower() in text.lower()
        else:
            saved = bool(db.value(check, phone))
        ok = all(delivered) and saved
        failures += not ok
        why = "" if ok else ("  ← not delivered" if not all(delivered) else "  ← not saved / wrong reply")
        print(f"  {'✓' if ok else '✗'} {label:<40} {replies[0].text.splitlines()[0][:64]}{why}")
        for extra in [ln for r in replies for ln in r.text.splitlines()[1:] if ln.strip()][:2]:
            print(f"  {'':<42} {extra[:64]}")
        buttons = [b for r in replies for b, _ in r.buttons] or buttons
        await asyncio.sleep(1.5)   # keep the chat readable on your phone
    return failures


async def main(keep: bool) -> None:
    for name in ("WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_APP_SECRET", "OPENAI_API_KEY"):
        if not core.env(name):
            sys.exit(f"Fill {name} in .env first.")
    phone = tester()
    core.set_user(phone)
    print(f"Testing with {phone[:-4]}****\n\n1. Webhook path")
    hook_ok = await webhook_check(phone)
    print("\n2. Conversation (watch your phone)")
    failures = await conversation(phone)
    if not keep:
        profile.delete_everything()
        print("\n3. Cleaned up: test data deleted")
    print(f"\n{'All good ✓' if hook_ok and not failures else f'{failures} reply(s) failed ✗'}")


if __name__ == "__main__":
    asyncio.run(main(keep="--keep" in sys.argv))
