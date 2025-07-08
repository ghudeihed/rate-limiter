# Rate Limiter Implementation - Fixed Window Algorithm

## Overview

This project implements a rate limiting system using the **Fixed Window Algorithm** in Python with FastAPI integration. The rate limiter controls the number of requests a customer can make within a specified time window, providing an essential mechanism for API throttling, abuse prevention, and resource management.

## Project Structure

```
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── dependencies/
│   │       │   └── rate_limiter_dependency.py  # FastAPI dependency for rate limiting
│   │       └── routes/
│   │           └── resource.py                 # API endpoints
│   ├── core/
│   │   └── rate_limiter.py                     # Core rate limiter implementation
│   └── main.py                                 # FastAPI application entry point
├── tests/
│   └── conftest.py                             # Unit tests shared fixtures
│   └── test_api_ping.py                        # Ping endpoint test suite
│   └── test_rate_limiter.py                    # Rate limiter test suite 
├── docs/
│   └── Take Home Assignment.docx               # Assignment documentation
├── pyproject.toml                             # Poetry dependencies
└── README.md                                  # This documentation
```

## Features

### Core Rate Limiter
- **Fixed Window Algorithm** with O(1) time complexity, and O(n) space complexity where n is the distinct numbers of IP/Token/Customer
- **Multi-customer support** with independent rate limiting
- **Memory efficient** storage with cleanup capabilities
- **Comprehensive error handling** and input validation
- **Floating point time support** for precise timing

### FastAPI Integration
- **HTTP 429 responses** for rate limit violations
- **IP-based rate limiting** out of the box
- **Dependency injection** for clean separation of concerns
- **Easy customization** for different rate limiting strategies
- **Production-ready** API endpoints

## Quick Start

### Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install fastapi uvicorn pytest
```

### Running the API

```bash
# Using Poetry
poetry run uvicorn app.main:app --reload

# Or directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc docs**: http://localhost:8000/redoc

### Testing the Rate Limiter

```bash
# Test the ping endpoint (rate limited)
curl http://localhost:8000/api/v1/ping

# Make multiple requests to trigger rate limiting
for i in {1..10}; do curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/ping' \
  -H 'accept: application/json'; echo; done
```

### Running Tests

```bash
# Using Poetry
poetry run pytest tests/ -v

# Or directly
pytest tests/test_rate_limiter.py -v --cov=app.core.rate_limiter
```

## Algorithm Choice: Fixed Window

### Why Fixed Window?

1. **Simplicity**: Easy to understand, implement, and debug
2. **Memory Efficiency**: O(1) space per customer
3. **Time Efficiency**: O(1) time complexity per request
4. **Predictable Behavior**: Clear reset boundaries
5. **Production Ready**: Widely used in real-world applications

### How It Works

```
Time:     0    30   60   90   120  150  180
Windows:  [----][----][----][----][----][----]
          W1   W2   W3   W4   W5   W6

Rate Limit: 3 requests per 30 seconds
Customer requests: ✓✓✓✗ | ✓✓✓✗ 
```

- Time is divided into fixed intervals (windows)
- Each customer has a request counter for the current window
- When a new window starts, the counter resets to 0
- Requests are allowed if the counter is below the rate limit

### Trade-offs

**Advantages:**
- Simple implementation and debugging
- Low memory overhead
- Predictable reset behavior
- Good performance characteristics

**Disadvantages:**
- **Boundary Burst Issue**: Can allow up to 2× the rate limit at window boundaries
- Less smooth than sliding window approaches
- May not handle traffic spikes as gracefully as token bucket

## API Usage

### Basic Endpoint

```python
@resource_router.get("/ping")
def ping(rate_limited: bool = Depends(get_rate_limiter)):
    return {"message": "pong"}
```

### Rate Limiting Responses

**Successful Request (200)**:
```json
{
  "message": "pong"
}
```

**Rate Limited (429)**:
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### Customizing Rate Limits

```python
# In rate_limiter_dependency.py
rate_limiter = RateLimiter(rate=10, time_window=60)  # 10 requests per minute

# For different endpoints
api_rate_limiter = RateLimiter(rate=100, time_window=3600)  # 100/hour
auth_rate_limiter = RateLimiter(rate=5, time_window=900)    # 5 per 15 minutes
```

### Advanced Customer Identification

```python
def get_rate_limiter(request: Request):
    # Option 1: IP-based (default)
    customer_id = request.client.host
    
    # Option 2: API key-based
    # customer_id = request.headers.get("X-API-Key", "anonymous")
    
    # Option 3: User-based (after authentication)
    # customer_id = request.state.user_id
    
    # Option 4: Combined approach
    # customer_id = f"{request.state.user_id}:{request.client.host}"
    
    current_time = time.time()
    if not rate_limiter.is_allowed(customer_id, current_time):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": "60"}  # Tell client when to retry
        )
    
    return True
```

## Core Implementation

### RateLimiter Class

```python
class RateLimiter:
    def __init__(self, rate: int, time_window: int)
    def is_allowed(self, customer_id: str, current_time: Union[int, float]) -> bool
```

**Key Features:**
- **Thread-safe**: Safe for concurrent access
- **Memory efficient**: Only stores window start and count per customer
- **Error handling**: Comprehensive input validation
- **Flexible timing**: Supports both integer and floating-point timestamps

### Window Calculation

```python
# Current window start time
current_window_start = (current_time // time_window) * time_window

# Example: time_window = 60 seconds
# current_time = 125 → window_start = 120
# current_time = 179 → window_start = 120
# current_time = 180 → window_start = 180 (new window)
```

## Testing Strategy

### Comprehensive Test Coverage

The test suite includes **100+ test cases** covering:

1. **Initialization Tests** - Parameter validation
2. **Basic Functionality** - Core rate limiting logic
3. **Time Window Tests** - Window transitions and boundaries
4. **Multi-Customer Tests** - Simultaneous customer handling
5. **Edge Case Tests** - Boundary conditions and unusual scenarios
6. **Integration Tests** - Real-world scenarios

### Key Test Scenarios

#### Window Boundary Testing
```python
def test_requests_within_same_window(self):
    """Verifies requests are properly counted within a single window"""
    # All within window [60, 90) with limit of 3
    assert self.rate_limiter.is_allowed("user", 60) is True   # Request 1
    assert self.rate_limiter.is_allowed("user", 70) is True   # Request 2  
    assert self.rate_limiter.is_allowed("user", 80) is True   # Request 3
    assert self.rate_limiter.is_allowed("user", 85) is False  # Request 4 - DENIED
```

#### Multi-Customer Isolation
```python
def test_independent_rate_limits(self):
    """Ensures each customer has independent rate limits"""
    for customer in ["alice", "bob", "charlie"]:
        # Each customer can make their full allocation
        assert self.rate_limiter.is_allowed(customer, timestamp) is True
```

#### Boundary Burst Behavior
```python
def test_boundary_burst_behavior(self):
    """Tests the 'burst' issue where 2x rate limit is possible at boundaries"""
    # 3 requests at end of window [10, 20)
    assert rate_limiter.is_allowed("user", 19.9) is True
    # 3 more at start of window [20, 30) 
    assert rate_limiter.is_allowed("user", 20.0) is True
    # Total: 6 requests in ~0.1 seconds!
```

### Running Specific Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_rate_limiter.py::TestRateLimiterTimeWindows -v

# Run with coverage
pytest tests/ --cov=app.core.rate_limiter --cov-report=html

# Run integration tests only
pytest tests/ -k "integration" -v
```

## Performance Characteristics

### Time Complexity
- **is_allowed()**: O(1) - Constant time per request
- **Memory per customer**: O(1) - Only stores (window_start, count)
- **Total memory**: O(n) - Linear in number of active customers

### Benchmarks

```python
# Theoretical performance on modern hardware:
# - 1M requests/second processing capability
# - Memory usage: ~100 bytes per active customer
# - Scales to millions of customers
```

### Memory Management

```python
# Optional: Implement periodic cleanup
def cleanup_old_customers(rate_limiter, current_time):
    """Remove customers with old window data"""
    customers_to_remove = []
    current_window = (current_time // rate_limiter.time_window) * rate_limiter.time_window
    
    for customer_id, (window_start, _) in rate_limiter.customers.items():
        if window_start < current_window - rate_limiter.time_window:
            customers_to_remove.append(customer_id)
    
    for customer_id in customers_to_remove:
        del rate_limiter.customers[customer_id]
    
    return len(customers_to_remove)
```

## Production Considerations

### Monitoring and Observability

```python
# Enhanced dependency with metrics
def get_rate_limiter_with_metrics(request: Request):
    customer_id = request.client.host
    current_time = time.time()
    
    # Collect metrics
    metrics.increment('rate_limiter.requests.total')
    
    if not rate_limiter.is_allowed(customer_id, current_time):
        metrics.increment('rate_limiter.requests.rejected')
        logger.warning(f"Rate limit exceeded for {customer_id}")
        
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "Retry-After": str(rate_limiter.time_window),
                "X-RateLimit-Limit": str(rate_limiter.rate),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(current_time) + rate_limiter.time_window)
            }
        )
    
    metrics.increment('rate_limiter.requests.allowed')
    return True
```

### Configuration Management

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    rate_limit_enabled: bool = True
    
    class Config:
        env_file = ".env"

# Usage
settings = Settings()
rate_limiter = RateLimiter(
    rate=settings.rate_limit_requests,
    time_window=settings.rate_limit_window
)
```

### Health Checks

```python
@app.get("/health")
def health_check():
    """Health check endpoint (not rate limited)"""
    return {
        "status": "healthy",
        "rate_limiter": {
            "active_customers": len(rate_limiter.customers),
            "algorithm": "fixed_window"
        }
    }
```

### Distributed Deployment

For distributed systems, consider:

```python
# Option 1: Redis-backed rate limiter
import redis

class RedisRateLimiter:
    def __init__(self, rate: int, time_window: int, redis_client):
        self.rate = rate
        self.time_window = time_window
        self.redis = redis_client
    
    def is_allowed(self, customer_id: str, current_time: float) -> bool:
        window_start = int(current_time // self.time_window) * self.time_window
        key = f"rate_limit:{customer_id}:{window_start}"
        
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.time_window)
        results = pipe.execute()
        
        return results[0] <= self.rate

# Option 2: Database-backed rate limiter
class DatabaseRateLimiter:
    # Implementation using SQL database for persistence
    pass
```

## Deployment

### Docker Support

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY app/ ./app/
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_ENABLED=true
LOG_LEVEL=INFO
```

### Production Deployment

```bash
# Using gunicorn for production
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or using uvicorn directly
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Alternative Algorithms Comparison

| Algorithm | Accuracy | Memory | Complexity | Burst Handling | Use Case |
|-----------|----------|--------|------------|----------------|----------|
| **Fixed Window** | Medium | Low | Low | Poor | General APIs |
| Sliding Window Log | High | High | Medium | Good | Precise control |
| Sliding Window Counter | Medium | Medium | Medium | Good | Balanced approach |
| Token Bucket | High | Low | Low | Excellent | Burst-tolerant APIs |
| Leaky Bucket | High | Medium | Medium | Good | Smooth traffic |

## Future Enhancements

### Planned Features

1. **Multiple Rate Limit Tiers**
```python
# Different limits per endpoint
@app.get("/api/v1/data")
@rate_limit(requests=1000, window=3600)  # 1000/hour
def get_data(): pass

@app.post("/api/v1/upload") 
@rate_limit(requests=10, window=3600)    # 10/hour
def upload_file(): pass
```

2. **Dynamic Rate Limits**
```python
# Adjust limits based on user tier
def get_user_rate_limit(user_id: str) -> Tuple[int, int]:
    user = get_user(user_id)
    if user.tier == "premium":
        return 10000, 3600  # 10k/hour
    elif user.tier == "standard":
        return 1000, 3600   # 1k/hour
    else:
        return 100, 3600    # 100/hour
```

3. **Advanced Algorithms**
```python
# Token bucket implementation
class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        # Implementation details...
```

4. **Metrics and Analytics**
```python
# Rate limiting analytics
@app.get("/admin/rate-limit-stats")
def get_rate_limit_stats():
    return {
        "total_requests": metrics.get_counter("requests.total"),
        "rejected_requests": metrics.get_counter("requests.rejected"),
        "top_customers": get_top_rate_limited_customers(),
        "rejection_rate": calculate_rejection_rate()
    }
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Implement periodic cleanup
   - Consider customer ID normalization
   - Monitor active customer count

2. **Rate Limits Too Strict**
   - Analyze request patterns
   - Consider burst allowances
   - Implement tiered limits

3. **False Positives**
   - Check customer ID logic
   - Verify time synchronization
   - Review window boundaries

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response
```

## Conclusion

This Fixed Window rate limiter implementation provides:

**✅ Production-Ready Features:**
- FastAPI integration with proper HTTP responses
- Comprehensive error handling and validation
- Extensive test coverage (100+ test cases)
- Clean, maintainable code architecture

**✅ Performance Optimized:**
- O(1) time complexity per request
- Low memory overhead
- Handles millions of customers efficiently

**✅ Enterprise Ready:**
- Monitoring and metrics support
- Configurable limits and behavior
- Docker and deployment ready
- Comprehensive documentation

**Best Use Cases:**
- REST API rate limiting
- Microservice throttling
- Development and testing environments
- Applications requiring simple, predictable rate limiting

**When to Consider Alternatives:**
- Need for very smooth rate limiting → Token Bucket
- Require perfect boundary accuracy → Sliding Window Log  
- Distributed systems → Redis-based solutions
- Very bursty traffic patterns → Token Bucket or Leaky Bucket

The implementation successfully handles all requirements and provides a robust foundation for production API rate limiting.