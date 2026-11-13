"""WhatsApp Cloud API (Meta, direct): parse webhooks, send messages and buttons, fetch media.

Free for replies to messages users send. Configure with:
WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_APP_SECRET, WHATSAPP_VERIFY_TOKEN.
Without a token, messages are printed to the log instead of sent (handy for local runs).
"""
import hashlib
import hmac
import logging
import time

import httpx

from server.core import env
from server.replies import Reply

log = logging.getLogger("spenzo")

BODY_LIMIT, TEXT_LIMIT, BUTTON_TITLE_LIMIT = 1024, 4096, 20
_image_ok: dict[str, tuple[float, bool]] = {}


async def image_reachable(url: str) -> bool:
    """WhatsApp drops a message whose image it can't fetch, so check first (cached for an hour)."""
    hit = _image_ok.get(url)
    if hit and time.time() - hit[0] < 3600:
        return hit[1]
    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
            resp = await client.head(url)
        ok = resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image/")
    except httpx.HTTPError:
        ok = False
    _image_ok[url] = (time.time(), ok)
    if not ok:
        log.warning("Image %s isn't reachable; sending without it.", url)
    return ok


def _graph() -> str:
    return f"https://graph.facebook.com/{env('WHATSAPP_API_VERSION', 'v25.0')}"


def _headers() -> dict:
    return {"Authorization": f"Bearer {env('WHATSAPP_TOKEN')}"}


def signature_ok(body: bytes, header: str) -> bool:
    """Meta signs each webhook with the app secret (X-Hub-Signature-256: sha256=<hex>)."""
    secret = env("WHATSAPP_APP_SECRET")
    if not secret:
        return env("ALLOW_UNSIGNED_WEBHOOKS") == "1"
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header or "")


def parse(payload: dict) -> list[dict]:
    """Flatten a webhook into messages: {id, phone, name, type, text, media_id, mime, button_id}."""
    out = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {c.get("wa_id"): c.get("profile", {}).get("name", "") for c in value.get("contacts", [])}
            for m in value.get("messages", []):
                kind = m.get("type")
                msg = {"id": m["id"], "phone": "+" + m["from"], "name": names.get(m["from"], ""),
                       "type": kind, "text": "", "media_id": "", "mime": "", "button_id": ""}
                if kind == "text":
                    msg["text"] = m["text"]["body"]
                elif kind in ("image", "audio", "document"):
                    media = m[kind]
                    msg.update(media_id=media["id"], mime=media.get("mime_type", ""), text=media.get("caption", ""))
                elif kind == "interactive":
                    picked = m["interactive"].get("button_reply") or m["interactive"].get("list_reply") or {}
                    msg.update(type="button", button_id=picked.get("id", ""), text=picked.get("title", ""))
                elif kind == "button":   # quick reply on a template message
                    msg.update(type="button", button_id=m["button"].get("payload", ""), text=m["button"].get("text", ""))
                out.append(msg)
    return out


def payload_for(to: str, reply: Reply) -> dict:
    base = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": to.lstrip("+")}
    if reply.link:
        label, url = reply.link
        return base | {"type": "interactive", "interactive": {
            "type": "cta_url", "body": {"text": reply.text[:BODY_LIMIT]},
            "action": {"name": "cta_url", "parameters": {"display_text": label[:BUTTON_TITLE_LIMIT], "url": url}}}}
    if reply.buttons:
        header = {"header": {"type": "image", "image": {"link": reply.image}}} if reply.image else {}
        return base | {"type": "interactive", "interactive": {
            **header, "type": "button", "body": {"text": reply.text[:BODY_LIMIT]},
            "action": {"buttons": [{"type": "reply", "reply": {"id": bid[:256], "title": title[:BUTTON_TITLE_LIMIT]}}
                                   for bid, title in reply.buttons[:3]]}}}
    if reply.image:
        return base | {"type": "image", "image": {"link": reply.image, "caption": reply.text[:BODY_LIMIT]}}
    return base | {"type": "text", "text": {"body": reply.text[:TEXT_LIMIT], "preview_url": False}}


async def send(to: str, reply: Reply) -> bool:
    """Send one reply. Returns True if WhatsApp accepted it (or it was only logged locally)."""
    if reply.image and env("WHATSAPP_TOKEN") and not await image_reachable(reply.image):
        reply = Reply(reply.text, reply.buttons, reply.link)
    if not env("WHATSAPP_TOKEN"):
        extras = [t for _, t in reply.buttons] + ([reply.link[0]] if reply.link else [])
        log.info("[WhatsApp -> %s] %s %s", to, reply.text, extras or "")
        return True
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{_graph()}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages",
                                 headers=_headers(), json=payload_for(to, reply))
    if resp.is_error:
        log.error("WhatsApp send failed %s: %s", resp.status_code, resp.text[:300])
        return False
    return True


async def typing(message_id: str) -> None:
    """Show blue ticks and 'typing…' while Spenzo thinks (clears on reply or after ~25s)."""
    if not env("WHATSAPP_TOKEN"):
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{_graph()}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", headers=_headers(),
                          json={"messaging_product": "whatsapp", "status": "read", "message_id": message_id,
                                "typing_indicator": {"type": "text"}})


async def download(media_id: str) -> tuple[bytes, str]:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        info = (await client.get(f"{_graph()}/{media_id}", headers=_headers())).raise_for_status().json()
        data = (await client.get(info["url"], headers=_headers())).raise_for_status().content
    return data, info.get("mime_type", "")
