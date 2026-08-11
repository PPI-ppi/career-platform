"""In-memory drop-in replacement for Redis when Redis is unavailable.

Provides the same async function signatures as redis.py using Python dicts.
"""
import time
from typing import Any

_store: dict[str, tuple[Any, float | None]] = {}  # key -> (value, expire_ts or None)
_counters: dict[str, tuple[int, float]] = {}       # key -> (count, expire_ts)


def _is_expired(expire_ts: float | None) -> bool:
    return expire_ts is not None and time.time() > expire_ts


def _get(key: str) -> Any | None:
    entry = _store.get(key)
    if entry is None:
        return None
    value, expire_ts = entry
    if _is_expired(expire_ts):
        del _store[key]
        return None
    return value


def _set(key: str, value: Any, ttl: int | None = None):
    expire_ts = time.time() + ttl if ttl else None
    _store[key] = (value, expire_ts)


def _delete(key: str):
    _store.pop(key, None)


# --- Connection (in-memory Redis-compatible client) ---

class _MemoryRedis:
    """Minimal async Redis-compatible client backed by the in-memory dict store.

    Lets call sites (e.g. feedback.py) use ``await r.get()`` / ``setex()`` /
    ``delete()`` without failing when Redis is unavailable.
    """

    async def get(self, key: str) -> Any:
        return _get(key)

    async def setex(self, key: str, ttl: int, value: Any):
        _set(key, value, ttl)

    async def delete(self, key: str):
        _delete(key)

    async def exists(self, key: str) -> bool:
        return _get(key) is not None

    async def expire(self, key: str, ttl: int):
        entry = _store.get(key)
        if entry is not None:
            _set(key, entry[0], ttl)

    async def incr(self, key: str) -> int:
        entry = _counters.get(key)
        now = time.time()
        if entry is None or now > entry[1]:
            _counters[key] = (1, now + 60)
            return 1
        count, expire_ts = entry
        _counters[key] = (count + 1, expire_ts)
        return count + 1

    async def hset(self, key: str, mapping: dict, **kwargs):
        obj = _get(key)
        if not isinstance(obj, dict):
            obj = {}
        obj.update(mapping)
        _set(key, obj, None)

    async def hgetall(self, key: str) -> dict:
        obj = _get(key)
        return obj if isinstance(obj, dict) else {}

    async def lpush(self, key: str, value: Any):
        obj = _get(key)
        if not isinstance(obj, list):
            obj = []
        obj.insert(0, value)
        _set(key, obj, None)


async def get_redis_pool():
    return None


async def get_redis():
    return _MemoryRedis()


async def close_redis():
    _store.clear()
    _counters.clear()


# --- Token blacklist ---

async def blacklist_token(token: str, expire_seconds: int):
    _set(f"blacklist:{token}", "1", expire_seconds)


async def is_token_blacklisted(token: str) -> bool:
    return _get(f"blacklist:{token}") is not None


# --- Rate limiter ---

async def check_rate_limit(user_key: str, limit: int, window: int = 60) -> bool:
    now = time.time()
    key = f"rate:{user_key}"
    entry = _counters.get(key)

    if entry is None or now > entry[1]:
        _counters[key] = (1, now + window)
        return True

    count, expire_ts = entry
    count += 1
    _counters[key] = (count, expire_ts)
    return count <= limit


# --- Agent result cache ---

async def cache_agent_result(agent_id: str, input_hash: str, value: str, ttl: int = 3600):
    _set(f"agent_cache:{agent_id}:{input_hash}", value, ttl)


async def get_cached_agent_result(agent_id: str, input_hash: str) -> str | None:
    return _get(f"agent_cache:{agent_id}:{input_hash}")


# --- Refresh token store ---

async def store_refresh_token(user_id: int, token: str, days: int = 7):
    _set(f"refresh:{token}", str(user_id), days * 86400)


async def get_refresh_user(token: str) -> int | None:
    uid = _get(f"refresh:{token}")
    return int(uid) if uid else None


async def revoke_refresh_token(token: str):
    _delete(f"refresh:{token}")
