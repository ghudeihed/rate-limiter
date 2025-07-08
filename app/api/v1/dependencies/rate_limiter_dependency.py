from functools import lru_cache
from fastapi import Depends, HTTPException, Request
from app.core.rate_limiter import RateLimiter
import time

@lru_cache()
def get_rate_limiter_instance():
    """Create singleton RateLimiter instance using lru_cache"""
    return RateLimiter(rate=5, time_window=60)

def get_customer_id(request: Request) -> str:
    """Get customer ID with fallback logic"""
    # Priority 1: Explicit client ID header
    client_id = request.headers.get("X-Client-ID")
    if client_id:
        return f"client:{client_id}"
    
    # Priority 2: Direct client host (for local testing)
    if hasattr(request, 'client') and request.client:
        return f"ip:{request.client.host}"
    
    # Fallback
    return "ip:unknown"

def get_rate_limiter(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter_instance)
):
    customer_id = get_customer_id(request)
    current_time = time.time()

    print(f"DEBUG: Customer ID: {customer_id}")
    print(f"DEBUG: RateLimiter customers: {limiter.customers}")

    if not limiter.is_allowed(customer_id, current_time):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    return True
