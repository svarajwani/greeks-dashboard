"""
producer.py

Polls Yahoo Finance for option quotes (including implied vol) using yfinance,
packages them into the {"quotes": {"quote": [...]}} structure, and
sends them to a Kafka topic for downstream processing.
"""

import os, json, time, re
import yfinance as yf
from confluent_kafka import Producer

OPTION_SYMBOLS = os.getenv("OPTION_SYMBOLS", "").split(",")
POLL_INTERVAL  = int(os.getenv("POLL_SEC", "2"))
KAFKA_BOOTSTRAP= os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC    = os.getenv("KAFKA_TOPIC", "quotes")

producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})

def parse_option_symbol(symbol: str):
    """
    Uses regex to capture:
+      1. root ticker (letters)
+      2. date YYMMDD
+      3. C/P flag
+      4. strike digits
    """

    m = re.match(r'^([A-Za-z]+)(\d{6})([CP])(\d+)$', symbol)
    if not m:
        raise ValueError(f"Invalid option symbol format: {symbol}")

    root, yymmdd, opt, strike_raw = m.groups()
    yy, mm, dd = yymmdd[:2], yymmdd[2:4], yymmdd[4:6]
    expiry = f"20{yy}-{mm}-{dd}"
    option_type = symbol[len(root) + 7]
    is_call = (option_type == "C")
    strike = float(strike_raw) / 1000.0
    return root, expiry, is_call, strike

if __name__ == "__main__":
    print(f"Starting yfinance producer: polling {len(OPTION_SYMBOLS)} symbols every {POLL_INTERVAL}s")
    while True:
        batch = []
        for symbol in OPTION_SYMBOLS:
            try:
                #parse components from symbol
                root, expiry, is_call, strike = parse_option_symbol(symbol)

                #get underlying price
                ticker = yf.Ticker(root)
                
                info = ticker.info  # one HTTP call, cached by yfinance
                underlying_price = info.get("regularMarketPrice") or info.get("previousClose")
                
                if underlying_price is None:
                    raise RuntimeError(f"No underlying price available for {root}")

                #get option chain for given expirt
                chain = ticker.option_chain(expiry)
                df = chain.calls if is_call else chain.puts

                #find specific contract row
                row = df[df["contractSymbol"] == symbol].iloc[0]

                #build tick
                tick = {
                    "symbol": symbol,
                    "underlying_price": underlying_price,
                    "strike" : row["strike"],
                    "expiration": expiry,
                    "iv": row["impliedVolatility"],
                    "option_type": "call" if is_call else "put",
                }
                batch.append(tick)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")

        #format ticks to expected kafka schema
        message = {"quotes": {"quote": batch}}
        payload = json.dumps(message)
        
        #produce to kafka
        try:
            producer.produce(KAFKA_TOPIC, payload)
            producer.poll(0) #background delivery
            print(f"[{time.strftime('%H:%M:%S')}] Pushed {len(batch)} ticks")
        except Exception as e:
            print("Delivery error:", e)

        time.sleep(POLL_INTERVAL)
