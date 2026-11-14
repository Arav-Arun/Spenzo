"""Live market data: currency rates, Indian stocks and mutual funds.

Sources are free and need no keys:
- Currency: Coinbase exchange rates
- NSE/BSE stocks: Yahoo Finance chart and search endpoints (unofficial)
- Mutual funds: mfapi.in (AMFI's daily NAVs)
Each price is cached for 15 minutes; a portfolio report doesn't need ticks.
"""
import time

from server.core import http

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
    """Units of each currency per 1 USD."""
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


# Names people still use for companies that were renamed or merged, and what the exchange calls them now.
OLD_NAMES = {"zomato": "Eternal", "policybazaar": "PB Fintech", "policy bazaar": "PB Fintech",
             "hdfc ltd": "HDFC Bank", "hdfc limited": "HDFC Bank"}


def find_stock(query: str) -> dict:
    """Best NSE (else BSE) match for a company name or ticker."""
    def fetch():
        search = OLD_NAMES.get(query.strip().lower(), query)
        quotes = http.get("https://query2.finance.yahoo.com/v1/finance/search",
                          params={"q": search, "quotesCount": 8, "newsCount": 0}).json().get("quotes", [])
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
