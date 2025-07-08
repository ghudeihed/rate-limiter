from fastapi import Depends, HTTPException, Request
from app.core.rate_limiter import RateLimiter
import time

# Initialize a shared rate limiter instance (e.g., 5 requests per 60 seconds)
rate_limiter = RateLimiter(rate=5, time_window=60)

def get_rate_limiter(request: Request):
    # IP-based limits utilizing request.client.host
    # In real apps, use something like request.headers["X-API-Key"] or request.state.user_id 
    customer_id = request.client.host
    
    current_time = time.time()
    if not rate_limiter.is_allowed(customer_id, current_time):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    return True
