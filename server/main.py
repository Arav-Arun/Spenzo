"""Spenzo for AI assistants (MCP): the same ledger inside Claude, ChatGPT, Cursor and others.

Hosted (for everyone): the bot server mounts this at /mcp. Each user gets a personal
URL by sending "connect ai" on WhatsApp: https://<server>/mcp?key=<personal key>.
The key decides whose data every tool call can see.

Local (for the owner): `uv run fastmcp run server/main.py` serves the same tools over
stdio, scoped to the WhatsApp number linked on this machine.
"""
import functools
import sys
from pathlib import Path

if not __package__:  # run as a file (`fastmcp run server/main.py`)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request

from server import auth, core
from server.tools import AI_TOOLS, LOCAL_ONLY_TOOLS

INSTRUCTIONS = (
    "Spenzo is the user's money buddy. It keeps one ledger: Spend (expenses, income, budgets), "
    "Split (who owes whom), Save (goals, stocks, mutual funds, crypto wallets, net worth). Answer "
    "money questions from these real numbers. Amounts are INR unless stated. Log expenses without "
    "asking for confirmation; find a transaction with search_transactions before editing it. "
    "Report investment facts only, never buy/sell advice. Dates are in India time: leave date "
    "arguments empty to mean the current month, and use the 'today' a tool returns rather than "
    "guessing today's date."
)


def _key_from_request() -> str | None:
    """The personal key on a hosted request, or None when running locally over stdio."""
    try:
        request = get_http_request()
    except RuntimeError:
        return None
    key = request.query_params.get("key") or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not key:
        raise PermissionError("Missing Spenzo key. Send 'connect ai' to Spenzo on WhatsApp to get your personal link.")
    return key


def _for_caller(tool):
    """Run a tool as whoever's key is on the request."""
    @functools.wraps(tool)
    def run(*args, **kwargs):
        key = _key_from_request()
        if key is not None:
            try:
                core.set_user(auth.read_token(key, "mcp"))
            except ValueError:
                raise PermissionError("This Spenzo link is no longer valid. Send 'connect ai' on WhatsApp for a new one.")
        return tool(*args, **kwargs)
    return run


def build(local: bool) -> FastMCP:
    server = FastMCP("Spenzo", instructions=INSTRUCTIONS)
    for tool in AI_TOOLS + (LOCAL_ONLY_TOOLS if local else []):
        server.tool(_for_caller(tool))
    return server


mcp = build(local=True)                                                    # stdio, for `fastmcp run`
hosted = build(local=False).http_app(path="/mcp", stateless_http=True)     # mounted by bot.py

if __name__ == "__main__":
    mcp.run()
