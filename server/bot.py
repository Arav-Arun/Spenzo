"""
Spenzo Bot Entry Point

This FastAPI application acts as a webhook receiver for Twilio WhatsApp messages.
It handles incoming texts and images, communicates with an LLM for intent recognition,
and utilizes MCP tools to interact with the database.
"""
import os
import json
import asyncio
import base64
import logging
import httpx
import requests
from fastapi import FastAPI, Request, Response
from openai import AsyncOpenAI
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CONFIGURATION & SETUP

# This section loads secret keys from the .env file and sets up the FastAPI application.
load_dotenv()
app = FastAPI()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("spenzo")

openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    twilio_client = None

# CONSTANTS & LLM RULES

WELCOME_MESSAGE = """👋 *Welcome to Spenzo!*

Your AI-powered personal finance command center. Just type naturally and I'll handle the rest!

💼 *Core Tracking*
📸 *Snap Receipts* — Send a photo of any bill to log it instantly.
💸 *Log Expenses* — "Spent ₹450 on Uber last night."
📊 *Summaries* — "How much did I spend on food this week?"
🔍 *Deep Search* — "Did I pay for Netflix last month?"
✏️ *Edit & Delete* — "Change that Uber expense to ₹500."
📈 *Crypto Prices* — "What's the live price of SOL?"
🔐 *Device Sync (OTP)* — "Link my WhatsApp +919876..."

⚡ *Automated Execution*
🍕 *Splitwise Killer* — "Dinner was ₹3000, split 3 ways — Arav owes me ₹1000."
💳 *1-Click UPI Collect* — "Who owes me?" → Instant UPI deep-link to collect.

🌐 *The Web3 Edge*
🔗 *Wallet Net Worth* — "Analyze wallet 0xabc..." → Live ETH/SOL balance in ₹.
💱 *DEX Swap Dispatcher* — "Swap 10 SOL for USDC." → Jupiter route + signing link.
🔥 *Gas Burn Analyzer* — "How much did I burn on gas?" → Real on-chain data.
🚜 *Staking Crawler* — "How much did I earn staking?" → Live LST positions.

Spenzo handles the math, FX conversions, and categories for you. Try it out!"""

SYSTEM_PROMPT = f"""You are Spenzo, a fast and sharp personal finance assistant on WhatsApp.
Today's date is {{today}}. Use this as the default date unless the user specifies one.
Be extremely concise. Plain text only - no Markdown, no asterisks, no bullet dashes.

CATEGORIES (auto-pick the closest - NEVER ask the user):
Food & Dining: Groceries, Restaurants, Coffee, Street Food, Fast Food, Delivery
Transportation: Fuel, Auto/Cab, Metro/Bus, Parking
Shopping: Clothing, Electronics, Accessories, Online Shopping
Entertainment: Movies, Events, Games, Subscriptions
Health: Medicine, Doctor, Gym
Housing: Rent, Utilities, Maintenance
Education: Courses, Books, Stationery
Miscellaneous: Gifts, Personal Care, Other

RULES:
1. Log requests ("spent X on Y", "X rupees for Z") → use the add_expense tool immediately, no questions.
2. After logging → confirm in 1 line ONLY: "✅ ₹120 logged - Samosa Chaat / Food & Dining"
3. For analytics/dashboard/summary requests → call summarize or list_expenses and present the breakdown clearly in 3-5 lines.
4. For greetings ("hi", "hello") → reply with the full welcome message.
5. Always reply in under 4 lines, except for welcome or summaries.
6. Use ₹ symbol for Indian Rupees, $ for USD.
7. NEVER output your internal thoughts or technical function names like "Call add_expense" in your responses to the user. Only output the final user-friendly message.
8. If a user asks to edit, update, or delete an expense, ALWAYS use the `search_expenses` tool first to find the `expense_id`. NEVER ask the user for the ID.

9. UPI IDs: If the user provides a string that looks like a UPI ID (e.g. name@bank, phone@upi, etc.), they are responding to your request for a UPI ID to generate collection links. Immediately call `list_debts` with that UPI ID!
10. Wallet Addresses: If the user provides a string that looks like a crypto wallet address (e.g. starts with `0x` for Ethereum, or a long base58 string for Solana), they are responding to your request to analyze their wallet. Immediately call `analyze_web3_wallet` with that address!

NEW CAPABILITIES (MATH & VISION):
- MULTI-CURRENCY: If the user mentions a foreign currency ($, €, £, etc.), natively convert it to INR (₹) using your best rough estimate of the current exchange rate. Pass the INR amount to `add_expense`, and explicitly state the original currency and your rough conversion rate in the `note` field.
- SPLITTING: If a user splits an expense (e.g. "spent 2000 on dinner, split 4 ways"), do the math yourself. Calculate their individual share (500) and pass THAT as the `amount` to `add_expense`. Note the split details ("Total 2000 split 4 ways") in the `note` field.
- RECEIPTS (VISION): If an image is provided in this prompt, it is a receipt. Extract the total amount, the merchant (as the category/subcategory), and the date (if visible) and log the expense. If the amount isn't clear, ask the user to clarify.

EXAMPLES OF DESIRED FINAL RESPONSES:
User: "Spent ₹150 on Samosa Chaat"
You: ✅ ₹150 logged - Samosa Chaat / Food & Dining

User: "Had coffee for $5"
You: ✅ ₹425 logged - Coffee / Food & Dining ($5 at ~₹85)

User: "Dinner was 3000 but we split it 3 ways"
You: ✅ ₹1000 logged - Dinner / Food & Dining (Total 3000 split 3 ways)
"""

# We will configure server_params dynamically inside call_llm_with_mcp

GREETING_KEYWORDS = {"hi", "hello", "hey", "start", "help", "helo", "hii", "hiii", "sup", "yo", "namaste", "info", "features"}

def is_greeting(text: str) -> bool:
    return text.strip().lower() in GREETING_KEYWORDS

# WHATSAPP COMMUNICATION

def send_whatsapp(to: str, body: str, media_url: str = None):
    """
    Send a WhatsApp message via Twilio.
    If media_url is provided, it attaches the image to the response.
    """
    logger.debug("send_whatsapp: to=%s has_media=%s client_ready=%s", to, bool(media_url), bool(twilio_client))
    if twilio_client and TWILIO_WHATSAPP_NUMBER:
        kwargs = {
            "from_": TWILIO_WHATSAPP_NUMBER,
            "body": body,
            "to": to
        }
        if media_url:
            kwargs["media_url"] = [media_url]
        msg = twilio_client.messages.create(**kwargs)
        logger.debug("send_whatsapp success: sid=%s status=%s", msg.sid, msg.status)
    else:
        logger.info("[WHATSAPP → %s]\n%s\nmedia=%s", to, body, media_url)


async def send_whatsapp_async(to: str, body: str, media_url: str = None):
    """Async wrapper that runs the blocking Twilio send in a thread executor."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: send_whatsapp(to, body, media_url=media_url))

# CORE AI LOGIC

async def call_llm_with_mcp(user_text: str, sender_phone: str = "", base64_image: str = None) -> str:
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    system = SYSTEM_PROMPT.replace("{today}", today)
    clean_phone = sender_phone.replace("whatsapp:", "").strip()
    if clean_phone:
        system += f"\n\nUSER PHONE NUMBER: {clean_phone} - ALWAYS pass this as phone_number when calling ANY tool."
        system += f"\n\nCRYPTO/WEB3 HINT: If the user asks about linking their Metamask, Solana, or Ethereum wallet, use the `analyze_web3_wallet` tool."

    # Pass only required env vars to the MCP subprocess (avoid leaking the full environment)
    _needed_keys = [
        "SUPABASE_URL", "SUPABASE_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_NUMBER", "ALCHEMY_API_KEY", "HELIUS_API_KEY",
        "PATH", "HOME", "VIRTUAL_ENV",
    ]
    env_vars = {k: os.environ[k] for k in _needed_keys if k in os.environ}
    if clean_phone:
        env_vars["LINKED_PHONE"] = clean_phone

    main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    server_params = StdioServerParameters(command="python", args=[main_py], env=env_vars)

    logger.debug("LLM: starting stdio_client subprocess...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            logger.debug("LLM: session created, initializing...")
            await session.initialize()
            logger.debug("LLM: session initialized, listing tools...")
            mcp_tools = await session.list_tools()
            logger.debug("LLM: got %d tools. Calling OpenAI...", len(mcp_tools.tools))

            oai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    }
                }
                for t in mcp_tools.tools
            ]

            content_blocks = []
            if user_text:
                content_blocks.append({"type": "text", "text": user_text})
            else:
                content_blocks.append({"type": "text", "text": "Here is an image. Extract the expense details and log it."})

            if base64_image:
                content_blocks.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })

            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": content_blocks}
            ]

            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=oai_tools if oai_tools else None,
                max_tokens=300
            )
            logger.debug("LLM: OpenAI response received.")

            msg = response.choices[0].message

            if getattr(msg, "tool_calls", None):
                messages.append(msg)
                for tc in msg.tool_calls:
                    logger.debug("LLM: calling tool '%s'...", tc.function.name)
                    args = json.loads(tc.function.arguments)
                    result = await session.call_tool(tc.function.name, arguments=args)
                    logger.debug("LLM: tool '%s' done.", tc.function.name)
                    result_string = str([item.text for item in result.content]) if hasattr(result, 'content') else str(result)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": tc.function.name,
                        "content": result_string
                    })

                final_response = await openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                logger.debug("LLM: final response received after tool calls.")
                return final_response.choices[0].message.content

            return msg.content

# WEBHOOK ENDPOINTS

@app.get("/")
async def health_check():
    """Provides a 200 OK status for Render's automated health checks to prevent deployment timeouts."""
    return {"status": "ok", "service": "Spenzo Bot"}

@app.post("/webhook")
async def twilio_webhook(request: Request):
    """
    This is the "front door" for WhatsApp. Whenever you send a message to the Spenzo bot,
    Twilio sends a request here.
    """
    try:
        form_data = await request.form()
        sender_id = form_data.get("From", "")
        text = form_data.get("Body", "").strip()
        
        logger.info("Webhook received. From=%s Body=%r", sender_id, text)

        # Check if the user sent a photo (receipt)
        num_media = int(form_data.get("NumMedia", "0"))
        media_url = form_data.get("MediaUrl0") if num_media > 0 else None
        
        if media_url:
            logger.debug("Media detected: %s", media_url)

        if (text or media_url) and sender_id:
            # GREETING LOGIC: direct synchronous reply
            if is_greeting(text) and not media_url:
                logger.debug("Greeting detected for %s", sender_id)
                banner = "https://www.spenzo.xyz/spenzo-banner.png"
                try:
                    await send_whatsapp_async(sender_id, WELCOME_MESSAGE, media_url=banner)
                    logger.debug("Welcome+banner sent OK")
                except Exception as e:
                    logger.warning("Welcome+banner failed (%s), trying text-only", e)
                    try:
                        await send_whatsapp_async(sender_id, WELCOME_MESSAGE)
                        logger.debug("Text-only welcome sent OK")
                    except Exception as e2:
                        logger.error("Text-only welcome also failed: %s", e2)
            else:
                # NON-GREETING: acknowledge and hand off to background task
                if not media_url:
                    await send_whatsapp_async(sender_id, "⚡ Got it! Processing...")
                else:
                    await send_whatsapp_async(sender_id, "📸 Received media! Processing receipt...")

                logger.debug("Scheduling background AI task...")
                asyncio.create_task(process_message(sender_id, text, media_url=media_url))
        else:
            logger.debug("Empty text and no media — ignoring.")

    except Exception:
        logger.exception("Top-level webhook error")

    return Response(content="<Response></Response>", media_type="application/xml")

async def download_twilio_media(url: str) -> str:
    """
    Download a Twilio WhatsApp media file and return it as a base64 string.
    Twilio media URLs redirect to a CDN - follow_redirects=True is essential.
    Falls back to a sync requests call via thread executor if async fails.
    """
    logger.debug("Downloading Twilio media from %s", url)

    # --- Attempt 1: async httpx with redirect following ---
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True  # CRITICAL: Twilio redirects to CDN
        ) as client:
            resp = await client.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            logger.debug("httpx response status=%s final_url=%s", resp.status_code, resp.url)
            if resp.status_code == 200 and len(resp.content) > 0:
                logger.debug("Download OK via httpx. Size=%d bytes", len(resp.content))
                return base64.b64encode(resp.content).decode("utf-8")
            logger.debug("httpx got %s, trying fallback...", resp.status_code)
    except Exception as e:
        logger.debug("httpx attempt failed: %s. Trying sync fallback...", e)

    # --- Attempt 2: sync requests via thread executor ---
    def sync_download():
        r = requests.get(
            url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=20,
            allow_redirects=True
        )
        logger.debug("requests fallback status=%s", r.status_code)
        if r.status_code == 200 and len(r.content) > 0:
            return base64.b64encode(r.content).decode("utf-8")
        return None

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, sync_download)
        if result:
            logger.debug("Download OK via requests fallback.")
            return result
    except Exception as e:
        logger.warning("requests fallback also failed: %s", e)

    logger.error("All media download attempts failed for %s", url)
    return None


async def process_message(sender_id: str, text: str, media_url: str = None):
    logger.debug("process_message started for %s. Text=%r Media=%s", sender_id, text, media_url)
    base64_img = None
    if media_url:
        base64_img = await download_twilio_media(media_url)
        if base64_img is None:
            # Download failed — tell the user instead of sending a confusing AI reply
            logger.warning("Media download failed for %s, sending error message.", sender_id)
            await send_whatsapp_async(
                sender_id,
                "📸 Couldn't read the image (download failed). Please try sending the receipt again!"
            )
            return

    try:
        logger.debug("calling call_llm_with_mcp with 45s timeout...")
        # If image is present, always prepend the receipt instruction
        effective_text = text
        if base64_img:
            effective_text = f"[Receipt image attached] {text}" if text else "[Receipt image attached] Please extract the expense details and log it."
        reply_text = await asyncio.wait_for(
            call_llm_with_mcp(effective_text, sender_phone=sender_id, base64_image=base64_img),
            timeout=45.0
        )
        logger.debug("AI reply ready. Sending...")
        await send_whatsapp_async(sender_id, reply_text)
        logger.info("Response sent to %s", sender_id)
    except asyncio.TimeoutError:
        logger.error("call_llm_with_mcp timed out after 45s for %s", sender_id)
        await send_whatsapp_async(sender_id, "⏱️ That took too long — please try again!")
    except Exception:
        logger.exception("Error in process_message for %s", sender_id)
        await send_whatsapp_async(sender_id, "⚠️ Spenzo hit a snag. Please try again!")
