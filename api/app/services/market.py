import logging, re, requests, yfinance as yf
from datetime import datetime

logger = logging.getLogger(__name__)

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
    response = requests.get(url, params={"symbols": ",".join(roots)})
    response.raise_for_status()
    try:
        data = response.json()
    except ValueError as exc:
        snippet = response.text[:200]
        logger.error(
            "Failed to decode JSON from %s: status %s, body %r",
            url,
            response.status_code,
            snippet,
        )
        raise ValueError(
            f"Failed to decode JSON from {url}: status {response.status_code}, body: {snippet}"
        ) from exc

    result = data.get("quoteResponse", {}).get("result", [])
    if not result:
        logger.warning(
            "No price data returned from %s for symbols %s; falling back to yfinance",
            url,
            roots,
        )
        price_map: dict[str, float] = {}
        for root in roots:
            try:
                price = yf.Ticker(root).info.get("regularMarketPrice")
            except Exception as exc:  # pragma: no cover - network errors
                logger.error("yfinance failed for %s: %s", root, exc)
                continue
            if price is not None:
                price_map[root] = price
        return price_map

    return {d["symbol"]: d["regularMarketPrice"] for d in result}
