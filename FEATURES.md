# Spenzo: The Complete Feature Guide

Spenzo operates across three main pillars: **Core Financial Tracking**, **Automated Execution**, and **The Web3 Edge**.

Below is an exhaustive reference manual of all **11 features** currently active in the Spenzo FastMCP engine, including exact real-world prompts and the direct programmatic output you can expect.

---

## 1. Core Financial Tracking

### 1.1 Natural Language Expense Logging

- **Description:** Log daily expenses directly via conversational text. The system extracts the date, normalizes the category against standard ledgers, and upserts to Supabase.
- **User Prompt:** _"Spent ₹450 on an Uber home last night."_
- **Expected Response:** `"✅ Logged ₹450 under 'Transportation > Ride Share' for Yesterday. Note: Uber home."`

### 1.2 Multi-Format Expense Summaries

- **Description:** Retrieve real-time data aggregations and time-bound summaries directly in chat.
- **User Prompt:** _"How much have I spent on Food this week?"_
- **Expected Response:** `"📊 This week, you have spent a total of ₹1,850 on 'Food & Dining'."`

### 1.3 Deep Search & Analytics

- **Description:** Query your entire PostgreSQL database using semantic keywords or strict date ranges to find specific outlays.
- **User Prompt:** _"Did I log a coffee purchase last month?"_
- **Expected Response:** `"☕ Yes, I found 3 entries for 'Coffee' last month totalling ₹450. The last one was ₹150 at Starbucks on the 14th."`

### 1.4 Ledger Management (Edit & Delete)

- **Description:** Modify past database entries based on conversational context.
- **User Prompt:** _"Wait, that Uber from yesterday was actually ₹500, not ₹450."_
- **Expected Response:** `"✏️ Updated! The 'Uber' expense on Feb 12th has been modified from ₹450 to ₹500."`

### 1.5 Vision OCR Receipt Parsing

- **Description:** The WhatsApp webhook automatically routes uploaded images for autonomous data extraction.
- **User Prompt:** _(User sends an image of a crumpled restaurant receipt)_
- **Expected Response:** `"📷 I've read the receipt for 'Taco Bell'. The total is $14.50. ✅ I have successfully logged this under 'Food & Dining'."`

### 1.6 Unified Device Sync (OTP Authentication)

- **Description:** Link your local Desktop Claude session directly to your isolated WhatsApp session so ledgers match across your phone and PC.
- **User Prompt:** _"Link my WhatsApp number +9198765XXXXX."_
- **Expected Response:** `"🔐 A 6-digit verification code has been sent via Twilio to +9198765XXXXX on WhatsApp. Please reply with the code."`

### 1.7 Live Multi-Currency Ticker

- **Description:** Ping real-time asset prices via CoinGecko directly in chat to calculate fiat-to-crypto expense conversions.
- **User Prompt:** _"What is the live price of Solana?"_
- **Expected Response:** `"📈 Live price of SOL: $142.50 USD (₹11,900 INR)."`

---

## 2. Automated Execution (State Mutation)

Unlike standard trackers, Spenzo acts as a Delegated Execution tool. It doesn't just read data, it dynamically constructs real-world payloads.

### 2.1 The Splitwise Killer (IOU Auto Ledger)

- **Description:** Maintain a "Receivable" database table. When invoked, it builds an official list of who owes you money.
- **User Prompt:** _"Arav owes me ₹500 for dinner."_
- **Expected Response:** `"✅ Debt Logged: Arav officially owes you ₹500 for 'dinner'. I will track this until settled!"`

### 2.2 Dynamic 1-Click UPI Dispatch

- **Description:** The system auto-generates deep-links and QR codes meant for 1-click fiat settlement.
- **User Prompt:** _"Who owes me money?"_
- **Expected Response:**
  `"💸 Your Outstanding Receivables:`
  `- Arav owes you ₹500 for 'dinner'.`
  `🔗 1-Click Auto-Collect: upi://pay?pa=...&am=500"`

---

## 🌐 3. The Web3 Edge (Crypto Intelligence)

Spenzo connects to Helius, Alchemy, and major Defi pipelines to serve essentially as an automated Bloomberg Terminal for Web3.

### 3.1 Live Crypto Net Worth

- **Description:** Connects to RPCs to fetch absolute token balances for EVM/Solana addresses and calculates real-world fiat value.
- **User Prompt:** _"Analyze my wallet 0xabc... what is my crypto worth right now?"_
- **Expected Response:** `"✅ Synced Ethereum Wallet 0xabc... Balances: 1.25 ETH. Net Worth: ~$3,500 USD (₹2,90,000 INR)."`

### 3.2 1-Click DEX Execution Dispatcher

- **Description:** The system dynamically pings the Jupiter v6 API for live routing slippage, and constructs a secure signing URL for non-custodial off-ramping.
- **User Prompt:** _"Swap 10 SOL for USDC."_
- **Expected Response:** `"💱 Routing 10 SOL secures exactly 1420.50 USDC (0.5% slippage). ⚡ Approve and execute this exact transaction instantly on your wallet: 🔗 https://jup.ag/swap/SOL-USDC?inAmount=10"`

### 3.3 The Gas Burn Analyzer (Real On-Chain)

- **Description:** Scrapes live on-chain history (Helius/Etherscan) to isolate network fees across a wallet and sum the total capital burned on execution.
- **User Prompt:** _"How much did I burn on gas?"_
- **Expected Response:** `"🔥 Scanned last 100 on-chain transactions: Total Gas Fees Paid: 0.124 ETH"`

### 3.4 The Staking Crawler (Real On-Chain)

- **Description:** Scans for Liquid Staking Tokens (stETH, JitoSOL) and native validator accounts to report active yield-bearing positions.
- **User Prompt:** _"How much interest did I earn staking?"_
- **Expected Response:** `"🚜 Detected: 1.25 stETH (Lido). Current APY: ~3.2%"`
