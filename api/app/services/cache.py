import redis, json
from ..config import settings

_r = redis.from_url(settings.redis_url, decode_responses = True)

def save(symbol: str, greeks: dict) -> None:
    _r.hset("greeks", symbol, json.dumps(greeks))

def snapshot() -> dict[str,dict]:
    return {k: json.loads(v) for k, v in _r.hgetall("greeks").items()}
