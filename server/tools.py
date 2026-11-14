"""The tools the WhatsApp agent can call (agent.py), grouped the way the product is:
Spend · Split · Save · See · You.
"""
import inspect
import typing

from pydantic import create_model

from server import auth, insights, profile, save, spend, split


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
        save.add_investment, save.remove_investment, save.portfolio, save.net_worth]
SEE = [insights.spending_chart, insights.wrapped]
YOU = [profile.remember, profile.forget, profile.set_nudges, profile.sign_out_everywhere, auth.dashboard_link]

CHAT_TOOLS = SPEND + SPLIT + SAVE + SEE + YOU + [delete_my_data]

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
