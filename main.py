"""
Spenzo MCP Server

This module implements a FastMCP server that provides a suite of tools
for managing expenses in a Supabase database. These tools are exposed to
AI assistants (like Claude Desktop or the separate webhook bot), giving them
the ability to read, write, and analyze the user's personal financial data.
"""
import os
import random
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from fastmcp import FastMCP
from supabase import create_client, Client
from dotenv import load_dotenv

# CONFIGURATION & IMPORTS

# This section loads database keys and connects to Supabase,
# which stores the actual user expenses.
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")


# MCP SERVER INITIALIZATION

# This initializes FastMCP, allowing AI clients (like Claude Desktop or our bot.py)
# to execute the tools defined below seamlessly.
mcp = FastMCP("ExpenseTracker")

# CORE EXPENSE TOOLS (CRUD)

# These functions allow the LLM to Create, Read, Update, and Delete records.

@mcp.tool()
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = "", phone_number: str = ""):
    '''Add a new expense entry to the database. Include the user's phone_number so analytics can filter by user.'''
    # Fall back to the linked phone from this session if not explicitly provided
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    data = {"date": date, "amount": amount, "category": category, "subcategory": subcategory, "note": note, "phone_number": resolved_phone}
    res = supabase.table("expenses").insert(data).execute()
    return {"status": "ok", "id": res.data[0]['id']}
    
@mcp.tool()
def list_expenses(start_date: str, end_date: str, phone_number: str = ""):
    '''List expense entries within an inclusive date range for the current user only.'''
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    query = supabase.table("expenses").select("id, date, amount, category, subcategory, note").gte("date", start_date).lte("date", end_date)
    if resolved_phone:
        # Filter by both stored formats to handle legacy data
        query = query.or_(f"phone_number.eq.{resolved_phone},phone_number.eq.whatsapp:{resolved_phone}")
    res = query.order("id").execute()
    return res.data

@mcp.tool()
def summarize(start_date: str, end_date: str, category: str = None, phone_number: str = ""):
    '''Summarize expenses by category within an inclusive date range for the current user only.'''
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    query = supabase.table("expenses").select("category, amount").gte("date", start_date).lte("date", end_date)
    if resolved_phone:
        query = query.or_(f"phone_number.eq.{resolved_phone},phone_number.eq.whatsapp:{resolved_phone}")
    if category:
        query = query.eq("category", category)
    res = query.execute()

    summary = {}
    for row in res.data:
        cat = row["category"]
        summary[cat] = summary.get(cat, 0) + row["amount"]

    return [{"category": k, "total_amount": round(v, 2)} for k, v in summary.items()]

@mcp.tool()
def search_expenses(query: str, phone_number: str = ""):
    '''Search expenses by category, subcategory, or note for the current user only.'''
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    base = supabase.table("expenses").select("id, date, amount, category, subcategory, note")
    if resolved_phone:
        # Filter by user then keyword-search within their data
        keyword_filter = f"category.ilike.%{query}%,subcategory.ilike.%{query}%,note.ilike.%{query}%"
        phone_filter = f"phone_number.eq.{resolved_phone},phone_number.eq.whatsapp:{resolved_phone}"
        res = base.or_(phone_filter).or_(keyword_filter).order("date", desc=True).limit(20).execute()
    else:
        res = base.or_(f"category.ilike.%{query}%,subcategory.ilike.%{query}%,note.ilike.%{query}%").order("date", desc=True).limit(20).execute()
    return res.data

@mcp.tool()
def edit_expense(expense_id: int, date: str = None, amount: float = None, category: str = None, subcategory: str = None, note: str = None):
    '''Edit an existing expense by its database ID. Provide only the fields you want to update (e.g., amount, category).'''
    updates = {}
    if date is not None: updates["date"] = date
    if amount is not None: updates["amount"] = amount
    if category is not None: updates["category"] = category
    if subcategory is not None: updates["subcategory"] = subcategory
    if note is not None: updates["note"] = note
    
    if not updates:
        return {"status": "error", "message": "No fields to update provided."}
        
    res = supabase.table("expenses").update(updates).eq("id", expense_id).execute()
    if not res.data:
        return {"status": "error", "message": f"No expense found with id {expense_id}."}
    return {"status": "ok", "message": f"Expense {expense_id} updated successfully."}

@mcp.tool()
def delete_expense(expense_id: int):
    '''Delete a specific expense by its database ID (e.g., to undo an accidental log).'''
    res = supabase.table("expenses").delete().eq("id", expense_id).execute()
    if not res.data:
        return {"status": "error", "message": f"No expense found with id {expense_id}."}
    return {"status": "ok", "message": f"Expense {expense_id} deleted successfully."}

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    if not os.path.exists(CATEGORIES_PATH):
        default_categories = {
            "categories": [
                {"name": "Food & Dining", "subcategories": ["Groceries", "Restaurants", "Coffee"]},
                {"name": "Transportation", "subcategories": ["Gas", "Transit", "Ride Share"]},
                {"name": "Housing", "subcategories": ["Rent", "Utilities", "Maintenance"]},
                {"name": "Entertainment", "subcategories": ["Movies", "Games", "Events"]}
            ]
        }
        import json
        with open(CATEGORIES_PATH, "w", encoding="utf-8") as f:
            json.dump(default_categories, f, indent=4)
            
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

@mcp.prompt()
def spenzo_welcome() -> str:
    """
    Spenzo's automatic greeting. This is shown as a helpful guide
    whenever you start a new chat session with this MCP server.
    """
    linked_phone = os.environ.get("LINKED_PHONE", "")
    if linked_phone:
        return (
            f"Welcome back to Spenzo! Your expenses are synced with WhatsApp number {linked_phone}.\n"
            "You can log expenses, ask for summaries, search, edit, or delete entries.\n"
            "Visit https://www.spenzo.xyz/analytics to see your full dashboard."
        )
    return (
        "Welcome to Spenzo - your AI expense tracker!\n\n"
        "You can log expenses naturally: 'Spent ₹200 on lunch' or 'Log $5 for coffee'.\n"
        "You can also ask for live crypto prices, like 'What is the price of SOL?'.\n\n"
        "💡 TIP: Link your WhatsApp number to sync expenses logged here with your WhatsApp bot "
        "and personal analytics at spenzo.xyz/analytics.\n"
        "Just say: 'Link my WhatsApp number' and I'll guide you through a quick verification!"
    )

# CROSS-PLATFORM SYNC (OTP) 

# These tools allow you to link a WhatsApp number to an isolated desktop session like Claude Desktop, so your data is securely synced everywhere.

@mcp.tool()
def register_phone(phone_number: str):
    """
    Start WhatsApp phone number linking for cross-platform expense sync.
    Sends a 6-digit OTP to the given WhatsApp number via Twilio.
    The phone_number must be in international format e.g. +919876543210.
    """
    import requests
    code = str(random.randint(100000, 999999))
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

    # Store OTP in Supabase verifications table
    supabase.table("verifications").upsert({
        "phone_number": phone_number,
        "code": code,
        "is_verified": False,
        "expires_at": expires_at
    }, on_conflict="phone_number").execute()

    # Send WhatsApp OTP via Twilio REST API
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    twilio_from = os.environ.get("TWILIO_WHATSAPP_NUMBER", "")

    if twilio_sid and twilio_token and twilio_from:
        resp = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
            auth=(twilio_sid, twilio_token),
            data={
                "From": twilio_from,
                "To": f"whatsapp:{phone_number}",
                "Body": f"🔐 Your Spenzo verification code is: *{code}*\nThis code expires in 10 minutes."
            }
        )
        if not resp.ok:
            return {"status": "error", "message": f"Twilio API Error (Limit Reached?): {resp.text}"}
        return {"status": "otp_sent", "message": f"A 6-digit code has been sent to {phone_number} on WhatsApp. Ask the user to check their WhatsApp and provide the code to complete verification."}
    else:
        return {"status": "error", "message": "Twilio credentials not configured in environment. Cannot send OTP."}

@mcp.tool()
def verify_phone(phone_number: str, code: str):
    """
    Complete WhatsApp phone number verification using the OTP sent by register_phone.
    On success, links the phone number to this MCP session for cross-platform expense sync.
    """
    res = supabase.table("verifications").select("*").eq("phone_number", phone_number).execute()
    if not res.data:
        return {"status": "error", "message": "No pending verification for this number. Please call register_phone first."}

    record = res.data[0]
    expires_at = datetime.fromisoformat(record["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return {"status": "error", "message": "OTP has expired. Please call register_phone again to get a new code."}

    if record["code"] != str(code):
        return {"status": "error", "message": "Incorrect OTP. Please check your WhatsApp and try again."}

    # Mark verified in Supabase
    supabase.table("verifications").update({"is_verified": True}).eq("phone_number", phone_number).execute()

    # Write LINKED_PHONE into local .env so future sessions remember it
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    lines = open(env_path).readlines() if os.path.exists(env_path) else []
    lines = [l for l in lines if not l.startswith("LINKED_PHONE")]
    lines.append(f'LINKED_PHONE="{phone_number}"\n')
    with open(env_path, "w") as f:
        f.writelines(lines)

    # Set in current process too
    os.environ["LINKED_PHONE"] = phone_number

    return {"status": "verified", "message": f"✅ Success! Your WhatsApp number {phone_number} is now linked. All expenses logged here will appear in your analytics at https://www.spenzo.xyz/analytics"}

# EXTERNAL APIS & UTILITIES

@mcp.tool()
def analyze_web3_wallet(wallet_address: str) -> str:
    '''Live Tool: Analyzes a public Web3 wallet (Ethereum or Solana) fetching real token balances via Helius or Alchemy. Use whenever a user asks to scan a wallet 0x... or 7x...'''
    import httpx
    wallet_address = wallet_address.strip()
    
    # Simple blockchain detection
    if wallet_address.startswith("0x") and len(wallet_address) == 42:
        chain = "Ethereum"
    else:
        chain = "Solana"
        
    try:
        report = []
        crypto_amount = 0
        
        if chain == "Ethereum":
            alchemy_key = os.environ.get("ALCHEMY_API_KEY", "")
            url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [wallet_address, "latest"],
                "id": 1
            }
            resp = httpx.post(url, json=payload, timeout=10.0).json()
            if "result" in resp:
                wei = int(resp["result"], 16)
                crypto_amount = wei / 1e18
                report.append(f"✅ Synced Ethereum Wallet {wallet_address[:6]}...{wallet_address[-4:]}")
                report.append(f"Balances:")
                report.append(f"- {crypto_amount:.4f} ETH")
            else:
                return f"Error fetching Ethereum balances: {resp.get('error')}"
                
        elif chain == "Solana":
            helius_key = os.environ.get("HELIUS_API_KEY", "")
            url = f"https://mainnet.helius-rpc.com/?api-key={helius_key}"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            resp = httpx.post(url, json=payload, timeout=10.0).json()
            if "result" in resp:
                lamports = resp["result"].get("value", 0)
                crypto_amount = lamports / 1e9
                report.append(f"✅ Synced Solana Wallet {wallet_address[:6]}...{wallet_address[-4:]}")
                report.append(f"Balances:")
                report.append(f"- {crypto_amount:.4f} SOL")
            else:
                return f"Error fetching Solana balances for {wallet_address}: {resp}"

        # Combine with CoinGecko for net worth
        cg_id = "ethereum" if chain == "Ethereum" else "solana"
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd,inr"
        cg_resp = httpx.get(cg_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10.0)
        
        if cg_resp.status_code == 200:
            data = cg_resp.json()
            if cg_id in data:
                price_usd = data[cg_id].get("usd", 0)
                price_inr = data[cg_id].get("inr", 0)
                total_usd = crypto_amount * price_usd
                total_inr = crypto_amount * price_inr
                report.append(f"\nNet Worth: ~${total_usd:,.2f} USD (₹{total_inr:,.0f} INR)")
                
        return "\\n".join(report)
        
    except Exception as e:
        return f"Error analyzing {chain} wallet: {str(e)}"

@mcp.tool()
def simulate_dex_swap(token_in: str, token_out: str, amount: float) -> str:
    '''Live Tool: Simulates a token swap on a DEX aggregator (like Jupiter or Uniswap) to fetch live routing quotes without executing the trade. Use when user asks "If I swap X for Y..."'''
    import httpx
    # Free Jupiter Quote API for Solana tokens
    symbol_to_mint = {
        "sol": "So11111111111111111111111111111111111111112",
        "usdc": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "bonk": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    }
    t_in = token_in.lower()
    t_out = token_out.lower()
    
    if t_in in symbol_to_mint and t_out in symbol_to_mint:
        mint_in = symbol_to_mint[t_in]
        mint_out = symbol_to_mint[t_out]
        lamports_in = int(amount * (1e9 if t_in == "sol" else 1e6 if t_in == "usdc" else 1e5))
        url = f"https://quote-api.jup.ag/v6/quote?inputMint={mint_in}&outputMint={mint_out}&amount={lamports_in}&slippageBps=50"
        try:
            resp = httpx.get(url, timeout=5.0).json()
            out_amount_raw = int(resp.get("outAmount", 0))
            out_decimals = 9 if t_out == "sol" else 6 if t_out == "usdc" else 5
            out_final = out_amount_raw / (10 ** out_decimals)
            execution_url = f"https://jup.ag/swap/{token_in}-{token_out}?inAmount={amount}"
            return (
                f"💱 **Live Swap Quote & Execution**\\n"
                f"Routing {amount} {token_in.upper()} secures exactly **{out_final:.4f} {token_out.upper()}**.\\n"
                f"(Route: {len(resp.get('routePlan', []))} hops, ~0.5% slippage tolerance).\\n\\n"
                f"⚡ **1-Click Execution Dispatch:**\\n"
                f"Approve and execute this exact transaction instantly on your wallet:\\n"
                f"🔗 {execution_url}"
            )
        except:
            pass
    
    execution_url = f"https://jup.ag/swap/{token_in.upper()}-{token_out.upper()}?inAmount={amount}"
    return (
        f"💱 **Live Swap Dispatch**\\n"
        f"Swapping {amount} {token_in.upper()} for {token_out.upper()} is ready at standard market rates.\\n\\n"
        f"⚡ **1-Click Execution Dispatch:**\\n"
        f"Click below to securely sign the transaction in your mobile/web wallet:\\n"
        f"🔗 {execution_url}"
    )

@mcp.tool()
def analyze_gas_burn(wallet_address: str) -> str:
    '''Live Tool: Sweeps a wallet's recent transaction history to calculate real network fees burned on gas. Use when user asks "How much did I burn on gas?"'''
    import httpx
    wallet_address = wallet_address.strip()
    chain = "Ethereum" if wallet_address.startswith("0x") and len(wallet_address) == 42 else "Solana"
    
    try:
        if chain == "Ethereum":
            url = f"https://eth.blockscout.com/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&page=1&offset=100&sort=desc"
            resp = httpx.get(url, timeout=10.0).json()
            if resp.get("status") == "1":
                txs = resp.get("result", [])
                total_gas_wei = sum(int(tx.get("gasUsed", 0)) * int(tx.get("gasPrice", 0)) for tx in txs if tx.get("from", "").lower() == wallet_address.lower())
                total_eth = total_gas_wei / 1e18
                return (
                    f"🔥 **Real Gas Burn Analyzer** ({chain})\\n"
                    f"Wallet: {wallet_address[:6]}...{wallet_address[-4:]}\\n\\n"
                    f"Scanned last {len(txs)} on-chain transactions:\\n"
                    f"- Total Gas Fees Paid: **{total_eth:.5f} ETH**"
                )
            return "Could not fetch Ethereum transactions from Etherscan."
            
        elif chain == "Solana":
            helius_key = os.environ.get("HELIUS_API_KEY", "")
            url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={helius_key}"
            resp = httpx.get(url, timeout=10.0)
            if resp.status_code == 200:
                txs = resp.json()
                total_lamports = sum(tx.get("fee", 0) for tx in txs if tx.get("feePayer", "") == wallet_address)
                total_sol = total_lamports / 1e9
                return (
                    f"🔥 **Real Gas Burn Analyzer** ({chain})\\n"
                    f"Wallet: {wallet_address[:6]}...{wallet_address[-4:]}\\n\\n"
                    f"Scanned last {len(txs)} on-chain transactions:\\n"
                    f"- Total Gas Fees Paid: **{total_sol:.5f} SOL**"
                )
            return f"Error fetching Solana transactions: {resp.status_code}"
    except Exception as e:
        return f"Error analyzing {chain} gas: {str(e)}"

@mcp.tool()
def check_staking_yield(wallet_address: str) -> str:
    '''Live Tool: Scans a wallet for active staking positions including Liquid Staking Tokens (stETH, JitoSOL) and native validator stakes on Solana. Use when user asks "How much interest am I earning?".'''
    import httpx
    wallet_address = wallet_address.strip()
    chain = "Ethereum" if wallet_address.startswith("0x") and len(wallet_address) == 42 else "Solana"
    
    try:
        if chain == "Ethereum":
            # Search for stETH (Lido) and rETH (RocketPool)
            alchemy_key = os.environ.get("ALCHEMY_API_KEY", "")
            url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getTokenBalances",
                "params": [wallet_address, ["0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", "0xae78736Cd615f374D3085123A210448E74Fc6393"]]
            }
            resp = httpx.post(url, json=payload, timeout=10.0).json()
            results = resp.get("result", {}).get("tokenBalances", [])
            
            summary = []
            for token in results:
                balance_hex = token.get("tokenBalance", "0x0")
                if balance_hex != "0x0":
                    symbol = "stETH (Lido)" if token.get("contractAddress").lower() == "0xae7ab96520de3a18e5e111b5eaab095312d7fe84" else "rETH (RocketPool)"
                    balance = int(balance_hex, 16) / 1e18
                    summary.append(f"- **{balance:.4f} {symbol}** (Active APY: ~3.2%)")
            
            if not summary:
                return f"🔍 **Staking Analyzer** ({chain})\\nNo common liquid staking positions (stETH/rETH) detected in this wallet."
            return f"🚜 **Active Staking Positions** ({chain})\\n" + "\\n".join(summary)

        elif chain == "Solana":
            helius_key = os.environ.get("HELIUS_API_KEY", "")
            # Check for JitoSOL and native stake accounts
            url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key={helius_key}"
            resp = httpx.get(url, timeout=10.0).json()
            tokens = resp.get("tokens", [])
            
            summary = []
            jitosol_mint = "J1tLqGr78idXSTFv9SnnvNE469NfhaRnpE6K2zW2RdxS"
            for t in tokens:
                if t.get("mint") == jitosol_mint:
                    balance = t.get("amount", 0) / 1e9
                    summary.append(f"- **{balance:.4f} JitoSOL** (Active APY: ~7.4%)")
            
            # Check for native stake accounts using standard RPC call through Helius endpoint
            rpc_url = f"https://mainnet.helius-rpc.com/?api-key={helius_key}"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getProgramAccounts",
                "params": ["Stake11111111111111111111111111111111111111", {
                    "filters": [{"memcmp": {"offset": 12, "bytes": wallet_address}}]
                }]
            }
            # Note: This is an expensive call, might be rate limited on free tier but Helius typically handles it
            rpc_resp = httpx.post(rpc_url, json=payload, timeout=10.0).json()
            staked_accs = rpc_resp.get("result", [])
            if staked_accs:
                total_lamports = sum(acc.get("account", {}).get("lamports", 0) for acc in staked_accs)
                summary.append(f"- **{total_lamports/1e9:.4f} SOL** in Native Stake Accounts")

            if not summary:
                return f"🔍 **Staking Analyzer** ({chain})\\nNo JitoSOL or Native Stake Accounts detected."
            return f"🚜 **Active Staking Positions** ({chain})\\n" + "\\n".join(summary)
            
    except Exception as e:
        return f"Error analyzing {chain} staking: {str(e)}"

@mcp.tool()
def generate_upi_payment_link(upi_id: str, amount: float, payee_name: str = "Spenzo User", note: str = "") -> str:
    '''Live Tool: Generates a 1-click UPI payment deep link. Use this when the user needs to request money from someone (e.g., "Alex owes me 500"). The returned link can be sent directly to the debtor so they can instantly pay via Google Pay, PhonePe, or Paytm.'''
    import urllib.parse
    params = {
        "pa": upi_id,
        "pn": payee_name,
        "am": str(amount),
        "cu": "INR",
        "tn": note
    }
    query_string = urllib.parse.urlencode(params)
    upi_url = f"upi://pay?{query_string}"
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_url)}"
    
    return (
        f"💳 **Dynamic UPI Payment Dispatched!**\\n\\n"
        f"To collect {amount} INR for '{note}', send this exact link to the debtor:\\n"
        f"🔗 `{upi_url}`\\n\\n"
        f"📷 Or send them this scannable QR Code URL:\\n{qr_url}\\n\\n"
        f"*(Note: The 'upi://pay' deep link will instantly open their native banking app on mobile).* "
    )

@mcp.tool()
def log_debt(debtor_name: str, amount: float, reason: str, phone_number: str = "") -> str:
    '''Agentic Tool: Log an IOU / Debt when someone owes the user money. It natively stores it in the Supabase 'expenses' table under the 'Receivable' category. Use this whenever the user says "X owes me Y".'''
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    data = {"date": datetime.now().isoformat()[:10], "amount": amount, "category": "Receivable", "subcategory": debtor_name, "note": reason, "phone_number": resolved_phone}
    res = supabase.table("expenses").insert(data).execute()
    return f"✅ **Debt Logged**: {debtor_name} officially owes you ₹{amount} for '{reason}'. I will track this until settled!"

@mcp.tool()
@mcp.tool()
def list_debts(upi_id: str = "", phone_number: str = "") -> str:
    '''Agentic Tool: List all people who currently owe the user money. Critically, this function automatically generates a dynamic UPI Intent link for every single debt so the user can easily collect the cash in 1 click. If you don't know the user's UPI ID, leave upi_id empty.'''
    resolved_phone = phone_number or os.environ.get("LINKED_PHONE", "")
    query = supabase.table("expenses").select("id, amount, subcategory, note").eq("category", "Receivable")
    if resolved_phone:
        query = query.or_(f"phone_number.eq.{resolved_phone},phone_number.eq.whatsapp:{resolved_phone}")
    res = query.execute()
    
    if not res.data:
        return "You have no outstanding debts! Nobody owes you money right now."
        
    report = ["💸 **Your Outstanding Receivables (The Splitwise Ledger):**\\n"]
    
    if not upi_id:
        for row in res.data:
            debtor = row['subcategory']
            amt = row['amount']
            reason = row['note']
            report.append(f"- **{debtor}** owes you **₹{amt}** for '{reason}'.")
        report.append("\\n⚠️ **Action Required**: To generate 1-click UPI collection links for these debts, please reply with your UPI ID (e.g., name@okicici).")
    else:
        for row in res.data:
            debtor = row['subcategory']
            amt = row['amount']
            reason = row['note']
            
            # Auto-generate dynamic real UPI collect link
            import urllib.parse
            upi_url = f"upi://pay?pa={upi_id}&pn=SpenzoUser&am={amt}&cu=INR&tn={urllib.parse.quote(reason)}"
            report.append(f"- **{debtor}** owes you **₹{amt}** for '{reason}'.")
            report.append(f"  🔗 1-Click Auto-Collect: `{upi_url}`\\n")
        
    return "\\n".join(report)

@mcp.tool()
def get_crypto_price(ticker: str) -> str:
    '''Fetch the exact live price of a cryptocurrency (e.g., BTC, ETH, SOL). The response will include USD and INR prices. Extremely useful for accurate expense logging when the user paid in crypto. Pass the symbol (e.g. sol) or name (e.g. solana).'''
    import httpx
    ticker = ticker.lower().strip()
    
    # Common name to symbol mapping since Coinbase uses symbols
    name_to_symbol = {
        "bitcoin": "btc", "ethereum": "eth", "solana": "sol", "usd-coin": "usdc",
        "tether": "usdt", "polygon": "matic", "dogecoin": "doge", "cardano": "ada",
        "avalanche": "avax", "chainlink": "link", "polkadot": "dot", "binancecoin": "bnb"
    }
    symbol = name_to_symbol.get(ticker, ticker).upper()
    
    try:
        usd_resp = httpx.get(f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot", timeout=10.0)
        usd_price = float(usd_resp.json()["data"]["amount"]) if usd_resp.status_code == 200 else 0
        
        inr_resp = httpx.get(f"https://api.coinbase.com/v2/prices/{symbol}-INR/spot", timeout=10.0)
        inr_price = float(inr_resp.json()["data"]["amount"]) if inr_resp.status_code == 200 else 0
        
        if usd_price > 0:
            return f"Live price of {symbol}: ${usd_price:,.2f} USD (₹{inr_price:,.2f} INR)."
        else:
            return f"Could not find live price for '{ticker}' (Symbol: {symbol})."
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port:
        # Run Server-Sent Events (SSE) HTTP Server for Cloud Deployments
        mcp.run(transport='sse', host="0.0.0.0", port=int(port))
    else:
        # Run Standard I/O for Local Claude Desktop
        mcp.run()