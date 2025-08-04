import os, re, asyncio, yfinance as yf
from datetime import datetime, UTC
from ..services.greeks import compute_greeks
from ..services.cache import save
from ..services.market import parse, last_prices
from ..config import settings

SYMBOLS = settings.option_symbols.split(",")
POLL_SEC = settings.poll_sec
RISK_FREE = settings.risk_free

async def poll_loop():
    while True:
        roots = list({parse(symbol)["root"] for symbol in SYMBOLS})
        price_map = last_prices(roots)
        for symbol in SYMBOLS:
            try:
                meta = parse(symbol)
                S = price_map[meta["root"]]
                ticker = yf.Ticker(meta["root"])
                chain = ticker.option_chain(meta["expiry"])
                df = chain.calls if meta["is_call"] else chain.puts
                row = df[df["contractSymbol"] == symbol]
                if row.empty:
                    continue
                row = row.iloc[0]
                sigma = row["impliedVolatility"]
                T = max(
                    (datetime.strptime(meta["expiry"], "%Y-%m-%d") - datetime.now(UTC)).days
                    / 365,
                    1e-6,
                )
                greeks = compute_greeks(S, meta["strike"], T, settings.risk_free, sigma, meta["is_call"])
                save(symbol, greeks)
            except Exception as e:
                print("Poll error:", e)
        
        print(datetime.now(UTC).strftime("%H:%M:%S"), "stored", len(SYMBOLS), "options")
        await asyncio.sleep(settings.poll_sec)

