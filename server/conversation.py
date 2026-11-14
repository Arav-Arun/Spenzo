"""One incoming message in, the replies out. Used by WhatsApp (bot.py) and the local simulator (chat.py)."""
import asyncio
import logging
from dataclasses import dataclass

from server import agent, auth, core, insights, profile, replies, statements
from server.replies import Reply

log = logging.getLogger("spenzo")
HELP_WORDS = {"help", "menu", "?", "options", "features"}
GREETINGS = {"hi", "hii", "hiii", "hello", "helo", "hey", "hey there", "start", "namaste", "yo", "sup", "hola"}


def _greeting(text: str) -> bool:
    return text.lower().strip("!.,? ") in GREETINGS
LOGIN_WORDS = {"login", "log in", "dashboard", "open dashboard", "sign in"}
UNDO_WORDS = {"undo", "undo that", "undo it", "delete that", "remove that", "cancel that", "galat", "galti"}
WRAPPED_WORDS = {"wrapped", "my wrapped", "month wrapped", "monthly wrapped"}


@dataclass
class Incoming:
    phone: str
    name: str = ""
    text: str = ""
    button_id: str = ""
    image: tuple[bytes, str] | None = None   # (bytes, mime)
    audio: tuple[bytes, str] | None = None
    pdf: tuple[bytes, str] | None = None     # (bytes, file name)
    forwarded: bool = False                  # forwarded from another chat


async def respond(msg: Incoming) -> list[Reply]:
    core.set_user(msg.phone)
    _, is_new = await asyncio.to_thread(profile.ensure, msg.name)
    first = [replies.welcome(msg.name)] if is_new else []
    if is_new and not (msg.image or msg.audio or msg.pdf) and (not msg.text.strip() or _greeting(msg.text)):
        return first
    if msg.pdf:
        return first + [await asyncio.to_thread(statements.from_pdf, *msg.pdf)]

    if msg.button_id:
        return first + [await asyncio.to_thread(replies.press, msg.button_id)]

    text = msg.text.strip()
    if statements.waiting_for_password() and text and " " not in text and len(text) <= 64:
        # Never reaches the AI or the chat history.
        return [await asyncio.to_thread(statements.with_password, text)]
    heard = ""
    if msg.audio:
        text = await agent.transcribe(*msg.audio)
        if not text:
            return [Reply("🎙️ I couldn't hear anything in that. Try again?")]
        heard = f"🎙️ _\"{text}\"_\n" if len(text) <= 120 else "🎙️ "

    word = text.lower().strip("!. ")
    if word in HELP_WORDS:
        return [replies.help_menu()]
    if word in UNDO_WORDS:
        return [await asyncio.to_thread(replies.undo_last)]
    if word in WRAPPED_WORDS:
        return [await asyncio.to_thread(insights.wrapped_reply)]
    if word in LOGIN_WORDS:
        return [Reply("Here's your dashboard. The link works for 15 minutes, then you stay signed in.",
                      link=("📊 Open dashboard", await asyncio.to_thread(auth.dashboard_url)))]

    answer = await agent.reply(text, msg.image, forwarded=msg.forwarded, quiet_ok=not msg.audio)
    answer.text = heard + answer.text
    return first + [answer] + ([answer.then] if answer.then else [])
