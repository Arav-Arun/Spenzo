"""WhatsApp Cloud API (Meta, direct): parse webhooks, send messages, buttons, reactions,
stickers and pictures, fetch media.

Free for replies to messages users send. Configure with:
WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_APP_SECRET, WHATSAPP_VERIFY_TOKEN.
Without a token, messages are printed to the log instead of sent (handy for local runs).
"""
import hashlib
import hmac
import logging
import time

import httpx

from server import brand
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
    """Flatten a webhook into messages: {id, phone, name, type, text, media_id, mime, filename,
    button_id, forwarded}."""
    out = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {c.get("wa_id"): c.get("profile", {}).get("name", "") for c in value.get("contacts", [])}
            for m in value.get("messages", []):
                kind = m.get("type")
                msg = {"id": m["id"], "phone": "+" + m["from"], "name": names.get(m["from"], ""),
                       "type": kind, "text": "", "media_id": "", "mime": "", "filename": "", "button_id": "",
                       "forwarded": bool(m.get("context", {}).get("forwarded")
                                         or m.get("context", {}).get("frequently_forwarded"))}
                if kind == "text":
                    msg["text"] = m["text"]["body"]
                elif kind in ("image", "audio", "document"):
                    media = m[kind]
                    msg.update(media_id=media["id"], mime=media.get("mime_type", ""), text=media.get("caption", ""),
                               filename=media.get("filename", ""))
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


def sticker_url(name: str) -> str:
    return f"{brand.WEB_URL}/stickers/baaz-{name}.webp"


def extras_for(to: str, reply: Reply, reply_to: str = "") -> tuple[list[dict], list[dict]]:
    """The messages that go before and after a reply's main bubble: a reaction, then a sticker."""
    base = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": to.lstrip("+")}
    before = [base | {"type": "reaction", "reaction": {"message_id": reply_to, "emoji": reply.react}}] \
        if reply.react and reply_to else []
    after = [base | {"type": "sticker", "sticker": {"link": sticker_url(reply.sticker)}}] if reply.sticker else []
    return before, after


async def _upload(client: httpx.AsyncClient, png: bytes) -> str:
    resp = await client.post(f"{_graph()}/{env('WHATSAPP_PHONE_NUMBER_ID')}/media", headers=_headers(),
                             data={"messaging_product": "whatsapp", "type": "image/png"},
                             files={"file": ("spenzo.png", png, "image/png")})
    return resp.raise_for_status().json()["id"]


async def send(to: str, reply: Reply, reply_to: str = "") -> bool:
    """Send one reply (and its reaction, picture and sticker). Returns True if WhatsApp accepted
    all of it, or it was only logged locally. reply_to is the user's message id, for reactions."""
    if reply.image and env("WHATSAPP_TOKEN") and not await image_reachable(reply.image):
        reply = Reply(reply.text, reply.buttons, reply.link, react=reply.react, sticker=reply.sticker, png=reply.png)
    if not env("WHATSAPP_TOKEN"):
        extras = [t for _, t in reply.buttons] + ([reply.link[0]] if reply.link else [])
        marks = [f"react {reply.react}"] * bool(reply.react) + [f"sticker {reply.sticker}"] * bool(reply.sticker) \
            + [f"picture {len(reply.png or b'') // 1024} KB"] * bool(reply.png)
        log.info("[WhatsApp -> %s] %s %s %s", to, reply.text, extras or "", marks or "")
        return True
    before, after = extras_for(to, reply, reply_to)
    main = []
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if reply.png:
                media_id = await _upload(client, reply.png)
                main.append({"messaging_product": "whatsapp", "recipient_type": "individual", "to": to.lstrip("+"),
                             "type": "image", "image": {"id": media_id, "caption": reply.text[:BODY_LIMIT]}})
                if reply.buttons or reply.link:
                    main.append(payload_for(to, Reply("👇", reply.buttons, reply.link)))
            elif reply.text:
                main.append(payload_for(to, reply))
        except httpx.HTTPError as e:
            log.error("WhatsApp picture upload failed: %s", e)
            main.append(payload_for(to, Reply(reply.text or "📊", reply.buttons, reply.link)))
        ok = True
        for payload in before + main + after:
            resp = await client.post(f"{_graph()}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages",
                                     headers=_headers(), json=payload)
            if resp.is_error:
                log.error("WhatsApp send (%s) failed %s: %s", payload["type"], resp.status_code, resp.text[:300])
                ok = False
    return ok


async def typing(message_id: str, show: bool = True) -> None:
    """Show blue ticks and 'typing…' while Spenzo thinks (clears on a reply or after ~25s).
    show=False only marks the message read: a ✅ reaction doesn't clear the typing dots."""
    if not env("WHATSAPP_TOKEN"):
        return
    body = {"messaging_product": "whatsapp", "status": "read", "message_id": message_id}
    if show:
        body["typing_indicator"] = {"type": "text"}
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{_graph()}/{env('WHATSAPP_PHONE_NUMBER_ID')}/messages", headers=_headers(), json=body)


async def download(media_id: str) -> tuple[bytes, str]:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        info = (await client.get(f"{_graph()}/{media_id}", headers=_headers())).raise_for_status().json()
        data = (await client.get(info["url"], headers=_headers())).raise_for_status().content
    return data, info.get("mime_type", "")
