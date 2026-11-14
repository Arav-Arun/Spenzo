"""Connect Meta's WhatsApp webhook to a running Spenzo bot, without clicking through the dashboard.

    ./scripts/dev.sh                                   # in one terminal: prints https://….trycloudflare.com/webhook
    uv run python scripts/whatsapp_connect.py https://….trycloudflare.com/webhook

Needs in .env: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_APP_ID, WHATSAPP_APP_SECRET,
WHATSAPP_VERIFY_TOKEN (and WHATSAPP_BUSINESS_ACCOUNT_ID if the token doesn't name its account). It:
  1. checks the token and phone number work,
  2. finds the WhatsApp Business Account the token belongs to,
  3. sets the app's webhook (Meta calls the bot once to verify it),
  4. subscribes the account so its messages reach the webhook.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from server.core import env

VERSION = env("WHATSAPP_API_VERSION", "v25.0")
GRAPH = f"https://graph.facebook.com/{VERSION}"


def need(*names: str) -> dict:
    missing = [n for n in names if not env(n)]
    if missing:
        sys.exit(f"Fill these in .env first: {', '.join(missing)}")
    return {n: env(n) for n in names}


def call(method: str, path: str, **params) -> dict:
    resp = httpx.request(method, f"{GRAPH}/{path.lstrip('/')}", params=params, timeout=30)
    data = resp.json()
    if resp.is_error or "error" in data:
        err = data.get("error", {})
        sys.exit(f"✗ {method} {path.split('?')[0]} failed: {err.get('message', resp.text)} (code {err.get('code')})")
    return data


def main(callback_url: str) -> None:
    v = need("WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_APP_ID", "WHATSAPP_APP_SECRET", "WHATSAPP_VERIFY_TOKEN")
    token, app_token = v["WHATSAPP_TOKEN"], f"{v['WHATSAPP_APP_ID']}|{v['WHATSAPP_APP_SECRET']}"

    number = call("GET", v["WHATSAPP_PHONE_NUMBER_ID"], fields="display_phone_number,verified_name,quality_rating",
                  access_token=token)
    print(f"✓ Phone number works: {number.get('display_phone_number')} ({number.get('verified_name')})")

    info = call("GET", "debug_token", input_token=token, access_token=app_token)["data"]
    if not info.get("is_valid"):
        sys.exit("✗ WHATSAPP_TOKEN has expired. Generate a new one on Step 1 · Try it out.")
    wabas = {t for s in info.get("granular_scopes", []) if s["scope"].startswith("whatsapp_business")
             for t in s.get("target_ids", [])}
    if env("WHATSAPP_BUSINESS_ACCOUNT_ID"):
        wabas = {env("WHATSAPP_BUSINESS_ACCOUNT_ID")}
    if not wabas:
        sys.exit("✗ Couldn't tell which WhatsApp account this token is for. Put its ID in .env as "
                 "WHATSAPP_BUSINESS_ACCOUNT_ID (WhatsApp Manager → Account tools → Phone numbers, or the "
                 "\"id\" in the test webhooks Meta shows on Step 1).")
    for waba in wabas:
        numbers = {p["id"] for p in call("GET", f"{waba}/phone_numbers", fields="id", access_token=token)["data"]}
        if v["WHATSAPP_PHONE_NUMBER_ID"] not in numbers:
            sys.exit(f"✗ WhatsApp account {waba} doesn't own phone number ID {v['WHATSAPP_PHONE_NUMBER_ID']}.")
    print(f"✓ Token is valid for app {info.get('app_id')}, WhatsApp account(s): {', '.join(sorted(wabas))}")

    call("POST", f"{v['WHATSAPP_APP_ID']}/subscriptions", object="whatsapp_business_account",
         callback_url=callback_url, verify_token=v["WHATSAPP_VERIFY_TOKEN"], fields="messages",
         access_token=app_token)
    print(f"✓ Webhook set to {callback_url} (Meta verified it with the bot)")

    for waba in sorted(wabas):
        call("POST", f"{waba}/subscribed_apps", access_token=token)
        print(f"✓ WhatsApp account {waba} subscribed: its messages now reach Spenzo")

    print("\nDone. Send 'hi' to Spenzo from your phone.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].startswith("https://"):
        sys.exit("Usage: uv run python scripts/whatsapp_connect.py https://YOUR-TUNNEL/webhook")
    main(sys.argv[1])
