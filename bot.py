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
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from twilio.rest import Client as TwilioClient
from supabase import create_client
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# CONFIGURATION & SETUP

# This section loads secret keys from the .env file, sets up the FastAPI application, and configures cross-origin sharing for the web dashboard.
load_dotenv()
app = FastAPI()

# Allow the analytics page (spenzo.xyz) to call our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.spenzo.xyz", "https://spenzo.xyz", "http://localhost"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Supabase client for the analytics proxy endpoint
_supabase_url = os.environ.get("SUPABASE_URL", "")
_supabase_key = os.environ.get("SUPABASE_KEY", "")
sb = create_client(_supabase_url, _supabase_key) if _supabase_url and _supabase_key else None

openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
WEBSITE_URL = "https://www.spenzo.xyz"
ANALYTICS_URL = f"{WEBSITE_URL}/analytics"

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

📊 *Live Dashboard* — View your full analytics at spenzo.xyz/analytics

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
3. For analytics/dashboard requests → reply: "📊 View your full dashboard here: {ANALYTICS_URL}"
4. For summaries → call summarize or list_expenses and present results clearly in 3-5 lines.
5. For greetings ("hi", "hello") → reply with the full welcome message.
6. Always reply in under 4 lines, except for welcome or summaries.
7. Use ₹ symbol for Indian Rupees, $ for USD.
8. NEVER output your internal thoughts or technical function names like "Call add_expense" in your responses to the user. Only output the final user-friendly message.
9. If a user asks to edit, update, or delete an expense, ALWAYS use the `search_expenses` tool first to find the `expense_id`. NEVER ask the user for the ID.

10. UPI IDs: If the user provides a string that looks like a UPI ID (e.g. name@bank, phone@upi, etc.), they are responding to your request for a UPI ID to generate collection links. Immediately call `list_debts` with that UPI ID!
11. Wallet Addresses: If the user provides a string that looks like a crypto wallet address (e.g. starts with `0x` for Ethereum, or a long base58 string for Solana), they are responding to your request to analyze their wallet. Immediately call `analyze_web3_wallet` with that address!

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
    print(f"DEBUG send_whatsapp called: to={to}, has_media={bool(media_url)}, client_ready={bool(twilio_client)}", flush=True)
    if twilio_client and TWILIO_WHATSAPP_NUMBER:
        kwargs = {
            "from_": TWILIO_WHATSAPP_NUMBER,
            "body": body,
            "to": to
        }
        if media_url:
            kwargs["media_url"] = [media_url]
        msg = twilio_client.messages.create(**kwargs)
        print(f"DEBUG send_whatsapp success: sid={msg.sid}, status={msg.status}", flush=True)
    else:
        print(f"[WHATSAPP → {to}]\n{body}\nmedia={media_url}\n", flush=True)

# CORE AI LOGIC

async def call_llm_with_mcp(user_text: str, sender_phone: str = "", base64_image: str = None) -> str:
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    system = SYSTEM_PROMPT.replace("{today}", today)
    clean_phone = sender_phone.replace("whatsapp:", "").strip()
    if clean_phone:
        system += f"\n\nUSER PHONE NUMBER: {clean_phone} - ALWAYS pass this as phone_number when calling ANY tool."
        system += f"\n\nCRYPTO/WEB3 HINT: If the user asks about linking their Metamask, Solana, or Ethereum wallet, use the `analyze_web3_wallet` tool."

    env_vars = {k: v for k, v in os.environ.items()}
    env_vars.pop("PORT", None)
    if clean_phone:
        env_vars["LINKED_PHONE"] = clean_phone

    server_params = StdioServerParameters(command="python", args=["main.py"], env=env_vars)

    print("DEBUG LLM: starting stdio_client subprocess...", flush=True)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("DEBUG LLM: session created, initializing...", flush=True)
            await session.initialize()
            print("DEBUG LLM: session initialized, listing tools...", flush=True)
            mcp_tools = await session.list_tools()
            print(f"DEBUG LLM: got {len(mcp_tools.tools)} tools. Calling OpenAI...", flush=True)

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
            print("DEBUG LLM: OpenAI response received.", flush=True)

            msg = response.choices[0].message

            if getattr(msg, "tool_calls", None):
                messages.append(msg)
                for tc in msg.tool_calls:
                    print(f"DEBUG LLM: calling tool '{tc.function.name}'...", flush=True)
                    args = json.loads(tc.function.arguments)
                    result = await session.call_tool(tc.function.name, arguments=args)
                    print(f"DEBUG LLM: tool '{tc.function.name}' done.", flush=True)
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
                print("DEBUG LLM: final response received after tool calls.", flush=True)
                return final_response.choices[0].message.content

            return msg.content

# WEBHOOK ENDPOINTS

@app.get("/")
async def health_check():
    """Provides a 200 OK status for Render's automated health checks to prevent deployment timeouts."""
    return {"status": "ok", "service": "Spenzo Bot"}

@app.get("/analytics/expenses")
async def analytics_expenses(phone: str = ""):
    """
    Proxy endpoint: fetches expenses for a phone number using server-side Supabase credentials.
    This prevents exposing the database keys directly to the frontend HTML/JS.
    """
    if not sb or not phone:
        return []
    clean = phone.strip().replace("whatsapp:", "")
    # Query both stored formats to handle legacy data
    r1 = sb.table("expenses").select("id,date,amount,category,subcategory,note,phone_number").eq("phone_number", clean).order("date", desc=True).limit(300).execute()
    r2 = sb.table("expenses").select("id,date,amount,category,subcategory,note,phone_number").eq("phone_number", f"whatsapp:{clean}").order("date", desc=True).limit(300).execute()
    merged = (r1.data or []) + (r2.data or [])
    merged.sort(key=lambda x: x.get("date", ""), reverse=True)
    return merged

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
        
        print(f"DEBUG: Webhook received. From: {sender_id}, Body: '{text}'", flush=True)

        # Check if the user sent a photo (receipt)
        num_media = int(form_data.get("NumMedia", "0"))
        media_url = form_data.get("MediaUrl0") if num_media > 0 else None
        
        if media_url:
            print(f"DEBUG: Media detected: {media_url}", flush=True)

        if (text or media_url) and sender_id:
            # GREETING LOGIC: direct synchronous reply
            if is_greeting(text) and not media_url:
                print(f"DEBUG: *** GREETING DETECTED for {sender_id} ***", flush=True)
                banner = "https://www.spenzo.xyz/spenzo-banner.png"
                loop = asyncio.get_event_loop()
                try:
                    await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, WELCOME_MESSAGE, media_url=banner))
                    print(f"DEBUG: Welcome+banner sent OK", flush=True)
                except Exception as e:
                    print(f"DEBUG: Welcome+banner FAILED ({e}), trying text-only", flush=True)
                    try:
                        await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, WELCOME_MESSAGE))
                        print(f"DEBUG: Text-only welcome sent OK", flush=True)
                    except Exception as e2:
                        print(f"DEBUG: Text-only also FAILED: {e2}", flush=True)
            else:
                # NON-GREETING: acknowledge and hand off to background task
                loop = asyncio.get_event_loop()
                if not media_url:
                    await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, "⚡ Got it! Processing..."))
                else:
                    await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, "📸 Received media! Processing receipt..."))

                print("DEBUG: Scheduling background AI task...", flush=True)
                asyncio.create_task(process_message(sender_id, text, media_url=media_url))
        else:
            print("DEBUG: Empty text and no media — ignoring.", flush=True)

    except Exception as top_e:
        import traceback
        print(f"DEBUG: TOP-LEVEL WEBHOOK ERROR: {top_e}", flush=True)
        traceback.print_exc()

    return Response(content="<Response></Response>", media_type="application/xml")

async def download_twilio_media(url: str) -> str:
    """
    Download a Twilio WhatsApp media file and return it as a base64 string.
    Twilio media URLs redirect to a CDN - follow_redirects=True is essential.
    Falls back to a sync requests call via thread executor if async fails.
    """
    print(f"DEBUG: Downloading Twilio media from {url}", flush=True)

    # --- Attempt 1: async httpx with redirect following ---
    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True  # CRITICAL: Twilio redirects to CDN
        ) as client:
            resp = await client.get(url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            print(f"DEBUG: httpx response status={resp.status_code} final_url={resp.url}", flush=True)
            if resp.status_code == 200 and len(resp.content) > 0:
                print(f"DEBUG: Download OK via httpx. Size={len(resp.content)} bytes", flush=True)
                return base64.b64encode(resp.content).decode("utf-8")
            else:
                print(f"DEBUG: httpx got {resp.status_code}, trying fallback...", flush=True)
    except Exception as e:
        print(f"DEBUG: httpx attempt failed: {e}. Trying sync fallback...", flush=True)

    # --- Attempt 2: sync requests via thread executor ---
    def sync_download():
        import requests
        r = requests.get(
            url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=20,
            allow_redirects=True
        )
        print(f"DEBUG: requests fallback status={r.status_code}", flush=True)
        if r.status_code == 200 and len(r.content) > 0:
            return base64.b64encode(r.content).decode("utf-8")
        return None

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sync_download)
        if result:
            print("DEBUG: Download OK via requests fallback.", flush=True)
            return result
    except Exception as e:
        print(f"DEBUG: requests fallback also failed: {e}", flush=True)

    print("DEBUG: All download attempts failed.", flush=True)
    return None


async def process_message(sender_id: str, text: str, media_url: str = None):
    print(f"DEBUG: process_message started for {sender_id}. Text: '{text}', Media: {media_url}", flush=True)
    base64_img = None
    if media_url:
        base64_img = await download_twilio_media(media_url)
        if base64_img is None:
            # Download failed — tell the user instead of sending a confusing AI reply
            print("DEBUG: Media download failed, sending error message.", flush=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: send_whatsapp(
                sender_id,
                "📸 Couldn't read the image (download failed). Please try sending the receipt again!"
            ))
            return

    try:
        print("DEBUG: calling call_llm_with_mcp with 45s timeout...", flush=True)
        # If image is present, always prepend the receipt instruction
        effective_text = text
        if base64_img:
            effective_text = f"[Receipt image attached] {text}" if text else "[Receipt image attached] Please extract the expense details and log it."
        reply_text = await asyncio.wait_for(
            call_llm_with_mcp(effective_text, sender_phone=sender_id, base64_image=base64_img),
            timeout=45.0
        )
        print(f"DEBUG: AI reply ready. Sending...", flush=True)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, reply_text))
        print(f"DEBUG: Response sent to {sender_id}", flush=True)
    except asyncio.TimeoutError:
        print("DEBUG ERROR: call_llm_with_mcp timed out after 45s!", flush=True)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, "⏱️ That took too long — please try again!"))
    except Exception as e:
        import traceback
        print(f"DEBUG ERROR in process_message: {e}", flush=True)
        traceback.print_exc()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: send_whatsapp(sender_id, "⚠️ Spenzo hit a snag. Please try again!"))
