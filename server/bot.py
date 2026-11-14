"""The server: WhatsApp webhook + dashboard API.

Run with: uvicorn server.bot:app
"""
import asyncio
import json
import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from server import api, brand, db, whatsapp
from server.conversation import Incoming, respond
from server.core import env
from server.replies import Reply

logging.basicConfig(level=env("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("spenzo")

app = FastAPI(title=brand.NAME)
app.add_middleware(CORSMiddleware, allow_origins=[brand.WEB_URL, "http://localhost:5173"],
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(api.router)

_background: set[asyncio.Task] = set()
_seen: dict[str, float] = {}   # Meta can deliver a webhook twice; answer each message once
SEEN_SECONDS = 3600


def _spawn(coro) -> None:
    task = asyncio.create_task(coro)
    _background.add(task)
    task.add_done_callback(_background.discard)


def _first_time(message_id: str) -> bool:
    now = time.time()
    for k in [k for k, t in _seen.items() if now - t > SEEN_SECONDS]:
        del _seen[k]
    if message_id in _seen:
        return False
    _seen[message_id] = now
    return True


async def handle(m: dict) -> None:
    try:
        _spawn(whatsapp.typing(m["id"]))
        msg = Incoming(phone=m["phone"], name=m["name"], text=m["text"], button_id=m["button_id"],
                       forwarded=m["forwarded"])
        timeout = 60
        if m["type"] == "image" or (m["type"] == "document" and m["mime"].startswith("image/")):
            msg.image = await whatsapp.download(m["media_id"])
        elif m["type"] == "document" and m["mime"] == "application/pdf":
            data, _ = await whatsapp.download(m["media_id"])
            msg.pdf = (data, m["filename"])
            timeout = 180   # a long statement takes a while to read
            await whatsapp.send(m["phone"], Reply("📄 Got it, reading that now…"))
        elif m["type"] == "audio":
            msg.audio = await whatsapp.download(m["media_id"])
        elif m["type"] not in ("text", "button"):
            await whatsapp.send(m["phone"], Reply("I can read text, photos, PDFs and voice notes. Try one of those!"))
            return
        for reply in await asyncio.wait_for(respond(msg), timeout=timeout):
            await whatsapp.send(m["phone"], reply, reply_to=m["id"])
    except asyncio.TimeoutError:
        log.error("Timed out answering %s", m["phone"])
        await whatsapp.send(m["phone"], Reply("⏱️ That took too long. Please try again!"))
    except Exception:
        log.exception("Failed to answer %s", m["phone"])
        await whatsapp.send(m["phone"], Reply("⚠️ Something went wrong on my side. Please try again!"))


@app.get("/")
def health():
    """Uptime pings land here, so a sleeping free-tier database wakes before users arrive."""
    try:
        db.value("select 1")
        database = "ok"
    except Exception as e:
        database = f"error: {type(e).__name__}"
    return {"service": brand.NAME, "database": database}


@app.get("/webhook")
def verify(request: Request):
    """Meta calls this once when you register the webhook URL."""
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == env("WHATSAPP_VERIFY_TOKEN") and env("WHATSAPP_VERIFY_TOKEN"):
        return PlainTextResponse(q.get("hub.challenge", ""))
    return Response(status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    if not whatsapp.signature_ok(body, request.headers.get("x-hub-signature-256", "")):
        return Response(status_code=403)
    for m in whatsapp.parse(json.loads(body or b"{}")):
        if _first_time(m["id"]):
            log.info("Message from %s (%s)", m["phone"], m["type"])
            _spawn(handle(m))
    return {"ok": True}   # answer Meta at once; replies go out from the background tasks
