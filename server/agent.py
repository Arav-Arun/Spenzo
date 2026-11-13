"""The money buddy behind WhatsApp: an OpenAI model calling Spenzo's tools in-process."""
import asyncio
import base64
import io
import json
import logging
import re
from functools import lru_cache

from openai import AsyncOpenAI

from server import brand, core, nudges, profile
from server.replies import Reply, logged, whatsapp_format
from server.spend import CATEGORIES
from server.tools import CHAT_TOOLS, EVENTS, schema

log = logging.getLogger("spenzo")

MODEL = core.env("OPENAI_MODEL", "gpt-4.1-mini")
TRANSCRIBE_MODEL = core.env("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
MAX_STEPS = 6

TOOLS = {fn.__name__: fn for fn in CHAT_TOOLS}
SCHEMAS = [schema(fn) for fn in CHAT_TOOLS]

SYSTEM_PROMPT = """You are {name}, the user's money buddy on WhatsApp. Today is {today}.

Be the friend who's great with money: warm, quick, honest, a little playful.
Reply in the language of the user's latest message only, ignoring earlier messages: English gets
English (the default, including short messages like "dinner 3000" or "salary 60k"). Use Hinglish
only when the latest message is Hindi written in English letters ("kitna kharcha hua?"), and
Hindi only when it's in Devanagari.

Work from their real numbers. Look things up with tools instead of guessing, and do the maths.
For "can I afford…" or "how much can I save…", check a typical month (last full month and this
month so far), income, budgets and goals, then answer yes / no / how, with numbers. If there's
less than a month of history, say so: ask about big fixed costs (rent, EMIs) or give a range
instead of a confident yes.
Always save things with tools before saying they're done: a spending limit ("keep food under
6k", "cap shopping at 5000") is set_budget, a new goal is add_goal, money in is add_income,
"X paid me back" is settle_debt. Never say something is set, saved or paid unless the tool call
succeeded.

What you keep track of:
- Spend: expenses, income, budgets. Log spends at once with add_expense; never ask which
  category. Foreign money: pass the original amount and currency.
- Split: "split with Arav and Riya" means the user plus each named person share equally (3000
  split with two friends = 1000 each: log 1000 with add_expense and 1000 for each friend with
  log_debt). Who owes whom works in both directions. For "who owes me", show the list and offer pay links
  if they share a UPI ID.
- Save: goals, investments (stocks, mutual funds, crypto wallets) and net worth. For a
  screenshot of holdings, call add_investment once per row. Report facts only: never tell the
  user to buy, sell or hold anything; explain trade-offs instead.
- You: save anything worth remembering with remember (name, income, salary day, people,
  plans) without asking.

Categories: {categories}
What you know about the user: {about}

Style: plain WhatsApp text, *bold* allowed, no headings, tables or markdown links. Usually
under 4 lines; lists and summaries can be longer. Rupees as ₹ with Indian grouping (₹1,23,456).
Never mention tool names or ids. Links and buttons from tools are attached automatically: don't
paste URLs. To change or delete something, find it with search_transactions first; never ask
for an id. A message that is only a UPI ID means "make pay links for my debts". A message that
is only a wallet address means "track this wallet". If a tool fails, say what to try instead."""


@lru_cache
def _client() -> AsyncOpenAI:
    return AsyncOpenAI()


def _system() -> str:
    user = profile.get() or {}
    about = [f"name {user['name']}" if user.get("name") else "",
             f"monthly income ₹{user['monthly_income']:,.0f}" if user.get("monthly_income") else "",
             f"salary on day {user['salary_day']}" if user.get("salary_day") else "",
             *(user.get("facts") or [])]
    return SYSTEM_PROMPT.format(name=brand.NAME, today=core.today(),
                                categories="; ".join(f"{c} ({ex})" for c, ex in CATEGORIES.items()),
                                about="; ".join(a for a in about if a) or "nothing yet")


async def _call(name: str, arguments: str) -> dict:
    try:
        result = await asyncio.to_thread(TOOLS[name], **json.loads(arguments or "{}"))
    except Exception as e:  # the model reads the error and explains it
        log.warning("tool %s failed: %s", name, e)
        return {"error": str(e)}
    return result if isinstance(result, dict) else {"result": result}


def _for_model(result: dict) -> str:
    visible = {k: v for k, v in result.items() if not k.startswith("_")}
    if "_link" in result or "_buttons" in result:
        visible["shown_to_user"] = "a button is attached to your reply"
    return json.dumps(visible, default=str, ensure_ascii=False)


# Messages that change something: an amount ("salary 60k"), or a word like paid / settle / save.
# Answering one of these without a tool call means nothing was saved, so we insist on a tool.
NEEDS_TOOL = re.compile(r"\d|\b(paid|pay|payed|settle[sd]?|back|wapas|lauta\w*|returned|add|log|set|save|move|"
                        r"delete|remove|undo)\b", re.I)


async def _think(messages: list[dict], text: str = "") -> tuple[Reply, set[str]]:
    events: set[str] = set()
    link, buttons = None, []
    for step in range(MAX_STEPS):
        choice = "none" if step == MAX_STEPS - 1 else "auto"
        resp = await _client().chat.completions.create(
            model=MODEL, messages=messages, tools=SCHEMAS, max_tokens=800, temperature=0.3, tool_choice=choice)
        msg = resp.choices[0].message
        if step == 0 and not msg.tool_calls and NEEDS_TOOL.search(text):
            # "salary 60k", "Arav paid me back": answering without a tool means nothing was saved.
            # Ask again, requiring a tool.
            resp = await _client().chat.completions.create(
                model=MODEL, messages=messages, tools=SCHEMAS, max_tokens=800, temperature=0.3, tool_choice="required")
            msg = resp.choices[0].message
        if not msg.tool_calls:
            return Reply(whatsapp_format(msg.content or "Sorry, I didn't catch that."), buttons, link), events

        messages.append(msg.model_dump(exclude_none=True))
        results = []
        for call in msg.tool_calls:
            result = await _call(call.function.name, call.function.arguments)
            results.append((call.function.name, result))
            if "error" not in result:
                if call.function.name in EVENTS:
                    events.add(EVENTS[call.function.name])
                if call.function.name == "add_income" and result.get("category") == "Salary":
                    events.add("salary")
                link = result.get("_link", link)
                buttons = result.get("_buttons", buttons)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": _for_model(result)})

        # A plain "spent X on Y" needs no second model call.
        if step == 0 and len(results) == 1 and results[0][0] == "add_expense" and "error" not in results[0][1]:
            return logged(results[0][1]), events
    return Reply("Sorry, that took too many steps. Try asking more simply?"), events


async def reply(text: str, image: tuple[bytes, str] | None = None) -> Reply:
    """Answer one message from the current user."""
    content = [{"type": "text", "text": text or "Here's a photo. If it's a bill, log it; if it's my holdings, add them."}]
    if image:
        data, mime = image
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64.b64encode(data).decode()}"}})
    history = await asyncio.to_thread(profile.history)
    messages = [{"role": "system", "content": await asyncio.to_thread(_system)}, *history,
                {"role": "user", "content": content}]

    answer, events = await _think(messages, text)
    nudge = await asyncio.to_thread(nudges.next_nudge, events)
    if nudge:
        answer.text += "\n\n" + nudge.text
        if nudge.buttons:
            answer.buttons = answer.buttons[:1] + nudge.buttons[:2]   # keep Undo, add the nudge's choices
        if nudge.link:
            answer.then = Reply("👇", link=nudge.link)
    await asyncio.to_thread(profile.save_exchange, text or "[sent a photo]", answer.text)
    return answer


async def transcribe(audio: bytes, mime: str) -> str:
    """Voice note -> text (English, Hindi and Hinglish)."""
    ext = {"audio/ogg": "ogg", "audio/mpeg": "mp3", "audio/mp4": "m4a", "audio/aac": "aac", "audio/amr": "amr"}
    f = io.BytesIO(audio)
    f.name = f"voice.{ext.get(mime.split(';')[0], 'ogg')}"
    result = await _client().audio.transcriptions.create(model=TRANSCRIBE_MODEL, file=f)
    return result.text.strip()
