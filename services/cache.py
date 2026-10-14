from datetime import UTC, datetime
from typing import cast

from services.redis_client import redis_client

CACHE_TTL_SECONDS = 60 * 60


def _cache_key(short_code: str) -> str:
    return f"url_shortener:link:{short_code}"


def get_cached_url(short_code: str) -> str | None:
    cached_url = redis_client.get(_cache_key(short_code))
    return cast(str | None, cached_url)


def cache_url(
    short_code: str,
    long_url: str,
    expires_at: datetime | None,
) -> None:
    ttl = CACHE_TTL_SECONDS

    if expires_at is not None:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        remaining_seconds = int((expires_at - datetime.now(UTC)).total_seconds())
        if remaining_seconds <= 0:
            return

        ttl = min(ttl, remaining_seconds)

    redis_client.setex(_cache_key(short_code), ttl, long_url)
