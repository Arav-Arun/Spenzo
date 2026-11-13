"""The one list of tools, shared by WhatsApp (agent.py) and AI assistants over MCP (main.py).

Grouped the way the product is: Spend · Split · Save · You.
"""
import inspect
import typing

from pydantic import create_model

from server import account, auth, profile, save, spend, split


def delete_my_data() -> dict:
    """Start deleting all of the user's Spenzo data. Shows Yes/Cancel buttons; nothing is
    deleted unless the user taps Yes."""
    return {"needs_confirmation": True,
            "_buttons": [("delete_all:yes", "Yes, delete all"), ("delete_all:no", "Cancel")]}


SPEND = [spend.add_expense, spend.add_income, spend.summarize, spend.list_transactions,
         spend.search_transactions, spend.edit_transaction, spend.delete_transaction,
         spend.set_budget, spend.budget_status]
SPLIT = [split.log_debt, split.list_debts, split.settle_debt]
SAVE = [save.add_goal, save.add_to_goal, save.goals_status, save.delete_goal,
        save.add_investment, save.add_wallet, save.remove_investment, save.portfolio, save.net_worth]
YOU = [profile.remember, profile.forget, profile.set_nudges, profile.sign_out_everywhere, auth.dashboard_link]

CHAT_TOOLS = SPEND + SPLIT + SAVE + YOU + [delete_my_data]
AI_TOOLS = SPEND + SPLIT + SAVE + [profile.remember, auth.dashboard_link]   # Claude, ChatGPT, Cursor…
LOCAL_ONLY_TOOLS = [account.link_whatsapp, account.finish_linking]           # owner's own machine, over stdio

# What each write means for nudges.
EVENTS = {"add_expense": "expense", "add_income": "income", "log_debt": "debt",
          "add_goal": "goal", "add_to_goal": "goal"}


def schema(fn) -> dict:
    """OpenAI function-calling schema built from a tool's signature and docstring."""
    hints = typing.get_type_hints(fn)
    fields = {name: (hints[name], ... if p.default is inspect.Parameter.empty else p.default)
              for name, p in inspect.signature(fn).parameters.items()}
    params = create_model(fn.__name__, **fields).model_json_schema()
    params.pop("title", None)
    for prop in params.get("properties", {}).values():
        prop.pop("title", None)
    return {"type": "function", "function": {"name": fn.__name__, "description": inspect.getdoc(fn) or "",
                                             "parameters": params}}
