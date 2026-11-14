"""Chat with Spenzo in your terminal, exactly as WhatsApp would, without WhatsApp.

    uv run python -m server.chat --memory          # throwaway local database, nothing to set up
    uv run python -m server.chat                   # the database in DATABASE_URL

Type messages normally. Buttons show as [1] [2] [3]: type the number to tap one.
/photo PATH sends an image, /voice PATH a voice note, /pdf PATH a PDF, /fwd TEXT a forwarded
message, /quit exits. Pictures Spenzo sends are saved to a temp file and the path is shown.
"""
import argparse
import asyncio
import mimetypes
import tempfile
import time
from pathlib import Path

from server.conversation import Incoming, respond

BOLD, DIM, GREEN, RESET = "\033[1m", "\033[2m", "\033[32m", "\033[0m"


def show(reply) -> list[str]:
    if reply.react:
        print(f"\n{DIM}         [reacted {reply.react} to your message]{RESET}", end="")
    if reply.png:
        path = Path(tempfile.gettempdir()) / f"spenzo-{int(time.time() * 1000)}.png"
        path.write_bytes(reply.png)
        print(f"\n{DIM}         [picture] {path}{RESET}", end="")
    if reply.image:
        print(f"\n{DIM}         [image] {reply.image}{RESET}", end="")
    if reply.text:
        print(f"\n{GREEN}Spenzo ›{RESET} " + reply.text.replace("\n", "\n         "))
    ids = []
    for i, (bid, title) in enumerate(reply.buttons, 1):
        print(f"         {BOLD}[{i}] {title}{RESET}")
        ids.append(bid)
    if reply.link:
        print(f"         {BOLD}[🔗 {reply.link[0]}]{RESET} {DIM}{reply.link[1]}{RESET}")
    if reply.sticker:
        print(f"{DIM}         [Baaz sticker: {reply.sticker}]{RESET}")
    return ids


def _file(path: str) -> tuple[bytes, str]:
    p = Path(path).expanduser()
    return p.read_bytes(), mimetypes.guess_type(p.name)[0] or "application/octet-stream"


async def main(phone: str, name: str) -> None:
    buttons: list[str] = []
    print(f"{DIM}Chatting as {name} ({phone}). /photo PATH · /voice PATH · /pdf PATH · /fwd TEXT · /quit{RESET}")
    while True:
        try:
            line = input(f"\n{BOLD}You ›{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not line:
            continue
        if line == "/quit":
            return
        msg = Incoming(phone=phone, name=name)
        if line.isdigit() and 0 < int(line) <= len(buttons):
            msg.button_id = buttons[int(line) - 1]
        elif line.startswith("/photo "):
            msg.image = _file(line[7:])
        elif line.startswith("/voice "):
            msg.audio = _file(line[7:])
        elif line.startswith("/pdf "):
            data, _ = _file(line[5:])
            msg.pdf = (data, Path(line[5:]).name)
        elif line.startswith("/fwd "):
            msg.text, msg.forwarded = line[5:], True
        else:
            msg.text = line
        try:
            buttons = []
            for reply in await respond(msg):
                buttons = show(reply) or buttons
        except Exception as e:
            print(f"{DIM}error: {e}{RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with Spenzo locally.")
    parser.add_argument("--memory", action="store_true", help="use a throwaway local database")
    parser.add_argument("--phone", default="+910000000000")
    parser.add_argument("--name", default="Arav")
    args = parser.parse_args()
    if args.memory:
        from server.localdb import throwaway_database
        with throwaway_database():
            asyncio.run(main(args.phone, args.name))
    else:
        asyncio.run(main(args.phone, args.name))
