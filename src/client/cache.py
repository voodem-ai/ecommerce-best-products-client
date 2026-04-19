"""Redis cache for prompt → recommendation responses."""

import hashlib
import json
from typing import Any

import redis.asyncio as redis
import structlog

from client.config import settings

log = structlog.get_logger()

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _pool
    if _pool is None:
        _pool = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _pool


async def close_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _hash_prompt(prompt: str) -> str:
    return f"rec:{hashlib.sha256(prompt.encode()).hexdigest()}"


async def cache_get_recommendation(prompt: str) -> str | None:
    r = await get_redis()
    try:
        return await r.get(_hash_prompt(prompt))
    except redis.ConnectionError:
        log.warning("cache_unavailable")
        return None


async def cache_set_recommendation(prompt: str, value: str) -> None:
    r = await get_redis()
    try:
        await r.setex(_hash_prompt(prompt), settings.REDIS_TTL, value)
    except redis.ConnectionError:
        log.warning("cache_unavailable")
