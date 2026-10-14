from services.redis_client import redis_client

COUNTER_KEY = "url_shortener:counter"


def get_next_id() -> int:
    """Atomically allocate and return the next URL identifier."""

    return int(redis_client.incr(COUNTER_KEY))
