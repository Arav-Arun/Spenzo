"""Live market data: currency rates, Indian stocks, mutual funds and crypto wallets.

Sources are free and need no keys (except Alchemy/Helius for wallets):
- Currency and crypto: Coinbase exchange rates
- NSE/BSE stocks: Yahoo Finance chart and search endpoints (unofficial)
- Mutual funds: mfapi.in (AMFI's daily NAVs)
Each price is cached for 15 minutes; a portfolio report doesn't need ticks.
"""
import re
import time

from server.core import env, http

CACHE_SECONDS = 15 * 60
_cache: dict[str, tuple[float, object]] = {}


def _cached(key: str, fetch, ttl: int = CACHE_SECONDS):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl:
        return hit[1]
    value = fetch()
    _cache[key] = (time.time(), value)
    return value


# --- Currency --------------------------------------------------------------

SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR", "rs": "INR", "rupees": "INR", "dollars": "USD"}


def _rates() -> dict[str, float]:
    """Units of each currency (fiat and crypto) per 1 USD."""
    def fetch():
        data = http.get("https://api.coinbase.com/v2/exchange-rates", params={"currency": "USD"}).json()
        return {k: float(v) for k, v in data["data"]["rates"].items()}
    return _cached("rates", fetch, ttl=60)


def inr_per(currency: str) -> float:
    code = SYMBOLS.get(currency.strip().lower(), currency.strip().upper())
    rate = _rates().get(code)
    if not rate:
        raise ValueError(f"I don't know the currency '{currency}'.")
    return _rates()["INR"] / rate


def to_inr(amount: float, currency: str) -> tuple[float, float]:
    """Convert to rupees. Returns (inr_amount, inr_per_unit)."""
    per_unit = inr_per(currency)
    return round(amount * per_unit, 2), per_unit


# --- Stocks and mutual funds -------------------------------------------------


def find_stock(query: str) -> dict:
    """Best NSE (else BSE) match for a company name or ticker."""
    def fetch():
        quotes = http.get("https://query2.finance.yahoo.com/v1/finance/search",
                          params={"q": query, "quotesCount": 8, "newsCount": 0}).json().get("quotes", [])
        indian = [q for q in quotes if q.get("exchange") in ("NSI", "BSE") and q.get("quoteType") in ("EQUITY", "ETF")]
        indian.sort(key=lambda q: q["exchange"] != "NSI")
        if not indian:
            raise ValueError(f"Couldn't find an Indian stock called '{query}'.")
        q = indian[0]
        return {"symbol": q["symbol"], "name": q.get("longname") or q.get("shortname") or q["symbol"]}
    return _cached(f"find_stock:{query.lower()}", fetch, ttl=24 * 3600)


def stock_price(symbol: str) -> dict:
    def fetch():
        meta = http.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                        params={"interval": "1d", "range": "5d"}).json()["chart"]["result"][0]["meta"]
        return {"price": meta["regularMarketPrice"], "previous_close": meta.get("chartPreviousClose")}
    return _cached(f"stock:{symbol}", fetch)


def find_fund(query: str) -> dict:
    """Best mfapi.in match for a fund name, preferring Direct Growth plans."""
    def fetch():
        funds = http.get("https://api.mfapi.in/mf/search", params={"q": query}).json()
        if not funds:
            raise ValueError(f"Couldn't find a mutual fund called '{query}'.")
        wants_regular = "regular" in query.lower()
        def score(f):
            n = f["schemeName"].lower()
            return ("growth" in n) * 2 + (("regular" in n) == wants_regular) + ("idcw" not in n)
        best = max(funds, key=score)
        return {"symbol": str(best["schemeCode"]), "name": best["schemeName"]}
    return _cached(f"find_fund:{query.lower()}", fetch, ttl=24 * 3600)


def fund_nav(code: str) -> dict:
    def fetch():
        latest = http.get(f"https://api.mfapi.in/mf/{code}/latest").json()["data"][0]
        return {"price": float(latest["nav"]), "as_of": latest["date"]}
    return _cached(f"fund:{code}", fetch)


# --- Crypto wallets ----------------------------------------------------------

ETH_ADDRESS = re.compile(r"^0x[0-9a-fA-F]{40}$")
SOL_ADDRESS = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
STETH = "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84"
RETH = "0xae78736Cd615f374D3085123A210448E74Fc6393"
JITOSOL = "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn"
STAKE_PROGRAM = "Stake11111111111111111111111111111111111111"


def chain_of(address: str) -> str:
    if ETH_ADDRESS.match(address.strip()):
        return "ethereum"
    if SOL_ADDRESS.match(address.strip()):
        return "solana"
    raise ValueError("That doesn't look like an Ethereum (0x…) or Solana wallet address.")


def _rpc(url: str, method: str, params: list):
    resp = http.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).json()
    if "error" in resp:
        raise RuntimeError(f"{method} failed: {resp['error'].get('message', resp['error'])}")
    return resp["result"]


def wallet_value(address: str) -> dict:
    """INR value of a public ETH or SOL wallet, staked ETH/SOL included."""
    address = address.strip()
    chain = chain_of(address)

    def fetch():
        coins: dict[str, float] = {}
        if chain == "ethereum":
            url = f"https://eth-mainnet.g.alchemy.com/v2/{env('ALCHEMY_API_KEY')}"
            coins["ETH"] = int(_rpc(url, "eth_getBalance", [address, "latest"]), 16) / 1e18
            for t in _rpc(url, "alchemy_getTokenBalances", [address, [STETH, RETH]])["tokenBalances"]:
                coins["ETH"] += int(t.get("tokenBalance") or "0x0", 16) / 1e18  # staked ETH, valued as ETH
        else:
            url = f"https://mainnet.helius-rpc.com/?api-key={env('HELIUS_API_KEY')}"
            coins["SOL"] = _rpc(url, "getBalance", [address])["value"] / 1e9
            accounts = _rpc(url, "getTokenAccountsByOwner", [address, {"mint": JITOSOL}, {"encoding": "jsonParsed"}])["value"]
            jito = sum(float(a["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] or 0) for a in accounts)
            if jito:
                coins["JITOSOL"] = jito
            stakes = _rpc(url, "getProgramAccounts", [STAKE_PROGRAM, {
                "encoding": "base64", "dataSlice": {"offset": 0, "length": 0},
                "filters": [{"memcmp": {"offset": 12, "bytes": address}}]}])
            coins["SOL"] += sum(s["account"]["lamports"] for s in stakes) / 1e9
        return coins

    coins = _cached(f"wallet:{address}", fetch)
    value = sum(amount * inr_per(coin) for coin, amount in coins.items() if amount)
    return {"chain": chain, "coins": {k: round(v, 6) for k, v in coins.items() if v}, "value": round(value, 2)}
