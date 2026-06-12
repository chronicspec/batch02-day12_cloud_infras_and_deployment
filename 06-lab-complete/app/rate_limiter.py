import time
import redis
from collections import defaultdict, deque
from fastapi import HTTPException
from app.config import get_settings

# Fallback in-memory just in case Redis is not available
_rate_windows: dict[str, deque] = defaultdict(deque)

try:
    settings = get_settings()
    r = redis.from_url(settings.redis_url) if settings.redis_url else None
    if r:
        r.ping() # test connection
except Exception:
    r = None

def check_rate_limit(user_id: str):
    settings = get_settings()
    if r is not None:
        now = int(time.time() * 1000)
        window_start = now - 60000
        key = f"rate_limit:{user_id}"
        
        pipeline = r.pipeline()
        pipeline.zremrangebyscore(key, 0, window_start)
        pipeline.zadd(key, {str(now): now})
        pipeline.zcard(key)
        pipeline.expire(key, 60)
        results = pipeline.execute()
        count = results[2]
        
        if count > settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
                headers={"Retry-After": "60"},
            )
    else:
        # Fallback to in-memory
        now = time.time()
        window = _rate_windows[user_id]
        while window and window[0] < now - 60:
            window.popleft()
        if len(window) >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
                headers={"Retry-After": "60"},
            )
        window.append(now)
