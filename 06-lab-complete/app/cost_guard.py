import time
import redis
from fastapi import HTTPException
from app.config import get_settings

# In-memory fallback
_daily_cost = 0.0
_cost_reset_day = time.strftime("%Y-%m-%d")

try:
    settings = get_settings()
    r = redis.from_url(settings.redis_url) if settings.redis_url else None
    if r:
        r.ping()
except Exception:
    r = None

def check_and_record_cost(user_id: str, input_tokens: int, output_tokens: int):
    settings = get_settings()
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    today = time.strftime("%Y-%m-%d")
    
    if r is not None:
        key = f"cost:{user_id}:{today}"
        # Increment cost
        current_cost = r.incrbyfloat(key, cost)
        r.expire(key, 86400 * 2) # keep for 2 days
        if current_cost >= settings.daily_budget_usd:
            raise HTTPException(
                status_code=402, 
                detail="Daily budget exhausted. Try tomorrow."
            )
    else:
        global _daily_cost, _cost_reset_day
        if today != _cost_reset_day:
            _daily_cost = 0.0
            _cost_reset_day = today
            
        if _daily_cost >= settings.daily_budget_usd:
            raise HTTPException(status_code=402, detail="Daily budget exhausted. Try tomorrow.")
        _daily_cost += cost

def check_budget(user_id: str):
    # Called before request processing
    settings = get_settings()
    today = time.strftime("%Y-%m-%d")
    if r is not None:
        key = f"cost:{user_id}:{today}"
        current_cost = float(r.get(key) or 0.0)
        if current_cost >= settings.daily_budget_usd:
            raise HTTPException(
                status_code=402, 
                detail="Daily budget exhausted. Try tomorrow."
            )
    else:
        global _daily_cost, _cost_reset_day
        if today != _cost_reset_day:
            _daily_cost = 0.0
            _cost_reset_day = today
        if _daily_cost >= settings.daily_budget_usd:
            raise HTTPException(status_code=402, detail="Daily budget exhausted. Try tomorrow.")

def get_daily_cost(user_id: str = "global") -> float:
    today = time.strftime("%Y-%m-%d")
    if r is not None:
        key = f"cost:{user_id}:{today}"
        return float(r.get(key) or 0.0)
    else:
        return _daily_cost
