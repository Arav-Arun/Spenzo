"""One incoming message in, the replies out. Used by WhatsApp (bot.py) and the local simulator (chat.py)."""
import asyncio
import logging
import re
from dataclasses import dataclass

from server import account, agent, auth, core, profile, replies
from server.replies import Reply

log = logging.getLogger("spenzo")
LINK_CODE = re.compile(r"^\s*link\s+(\d{6})\s*$", re.I)
HELP_WORDS = {"help", "menu", "?", "options", "features"}
GREETINGS = {"hi", "hii", "hiii", "hello", "helo", "hey", "hey there", "start", "namaste", "yo", "sup", "hola"}


def _greeting(text: str) -> bool:
    return text.lower().strip("!.,? ") in GREETINGS
LOGIN_WORDS = {"login", "log in", "dashboard", "open dashboard", "sign in"}
CONNECT_WORDS = {"connect ai", "connect my ai", "connect claude", "connect chatgpt", "connect cursor", "mcp"}


@dataclass
class Incoming:
    phone: str
    name: str = ""
    text: str = ""
    button_id: str = ""
    image: tuple[bytes, str] | None = None   # (bytes, mime)
    audio: tuple[bytes, str] | None = None


async def respond(msg: Incoming) -> list[Reply]:
    core.set_user(msg.phone)
    _, is_new = await asyncio.to_thread(profile.ensure, msg.name)
    first = [replies.welcome(msg.name)] if is_new else []
    if is_new and not msg.image and not msg.audio and (not msg.text.strip() or _greeting(msg.text)):
        return first

    if msg.button_id:
        return first + [await asyncio.to_thread(replies.press, msg.button_id)]

    text = msg.text.strip()
    heard = ""
    if msg.audio:
        text = await agent.transcribe(*msg.audio)
        if not text:
            return [Reply("🎙️ I couldn't hear anything in that. Try again?")]
        heard = f"🎙️ _\"{text}\"_\n" if len(text) <= 120 else "🎙️ "

    if (m := LINK_CODE.match(text)):
        ok = await asyncio.to_thread(account.claim_code, m.group(1))
        return [Reply("✅ Got it! Go back to Claude and say *done*." if ok else
                      "That code didn't work. Ask Claude for a new one.")]
    if text.lower().strip("!. ") in HELP_WORDS:
        return [replies.help_menu()]
    if text.lower().strip("!. ") in CONNECT_WORDS:
        return [Reply("🤖 Here's your private link to use Spenzo inside Claude, ChatGPT or Cursor. "
                      "Don't share it: it opens your money data.",
                      link=("🤖 Connect your AI", await asyncio.to_thread(auth.ai_connect_url)))]
    if text.lower().strip("!. ") in LOGIN_WORDS:
        return [Reply("Here's your dashboard. The link works for 15 minutes, then you stay signed in.",
                      link=("📊 Open dashboard", await asyncio.to_thread(auth.dashboard_url)))]

    answer = await agent.reply(text, msg.image)
    answer.text = heard + answer.text
    return first + [answer] + ([answer.then] if answer.then else [])
