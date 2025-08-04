import re, requests, yfinance as yf
from datetime import datetime

symbol_regex = re.compile(r'^([A-Za-z]+)(\d{6})([CP])(\d+)$')


def parse(symbol: str):
    m = symbol_regex.match(symbol)
    root, ymd, call_or_put, strike = m.groups()
    yy, mm, dd = ymd[:2], ymd[2:4], ymd[4:6]
    expiry = f"20{yy}-{mm}-{dd}"
    is_call = (call_or_put == "C")
    strike = float(strike) / 1000

    return dict(
        root=root,
        expiry=expiry,
        is_call=is_call,
        strike=strike,
    )

def last_prices(roots: list[str]) -> dict[str, float]:
    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    data = requests.get(url, params={"symbols": ",".join(roots)}).json()
    return {d["symbol"]: d["regularMarketPrice"] for d in data["quoteResponse"]["result"]}