from fastapi import Depends, HTTPException, Request
from app.core.rate_limiter import RateLimiter
import time

# Default rate limiter instance
def get_rate_limiter_instance():
    return RateLimiter(rate=5, time_window=60)

def get_rate_limiter(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter_instance)
):
    # Use header-based customer ID for testability
    customer_id = request.headers.get("X-Client-ID") or request.client.host
    
    current_time = time.time()

    if not limiter.is_allowed(customer_id, current_time):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    return True
