# Rate Limiter Implementation - Fixed Window Algorithm

## Overview

This project implements a rate limiting system using the **Fixed Window Algorithm** in Python. The rate limiter controls the number of requests a customer can make within a specified time window, providing an essential mechanism for API throttling, abuse prevention, and resource management.

## Algorithm Choice: Fixed Window

### Why Fixed Window?

I chose the Fixed Window algorithm for the following reasons:

1. **Simplicity**: Easy to understand and implement
2. **Memory Efficiency**: O(1) space per customer (only stores window start time and count)
3. **Time Efficiency**: O(1) time complexity per request
4. **Predictable Behavior**: Clear reset boundaries make it easier to reason about
5. **Production Ready**: Widely used in real-world applications

### How It Works

The Fixed Window algorithm divides time into fixed intervals (windows) and tracks the number of requests made within each window:

```
Time:     0    30   60   90   120  150  180
Windows:  [----][----][----][----][----][----]
          W1   W2   W3   W4   W5   W6
```

- Each window has a fixed duration (e.g., 60 seconds)
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

## Implementation Details

### Core Components

#### RateLimiter Class
```python
class RateLimiter:
    def __init__(self, rate: int, time_window: int)
    def is_allowed(self, customer_id: str, current_time: int) -> bool
    def get_customer_status(self, customer_id: str, current_time: int) -> Dict
    def cleanup_old_entries(self, current_time: int) -> int
```

#### Data Structure
- **Storage**: Dictionary mapping `customer_id -> (window_start, request_count)`
- **Window Calculation**: `window_start = (current_time // time_window) * time_window`
- **Memory Management**: Automatic cleanup of old entries

### Key Features

1. **Multi-Customer Support**: Independent rate limiting per customer
2. **Input Validation**: Comprehensive parameter validation
3. **Error Handling**: Graceful handling of edge cases
4. **Status Monitoring**: Built-in status reporting for debugging
5. **Memory Management**: Cleanup mechanism for old entries
6. **Floating Point Time**: Supports fractional timestamps

## Usage Examples

### Basic Usage
```python
# Create rate limiter: 5 requests per 60 seconds
rate_limiter = RateLimiter(5, 60)

# Check if request is allowed
if rate_limiter.is_allowed("user_123", current_time):
    # Process request
    process_request()
else:
    # Reject request
    return "Rate limit exceeded"
```

### Production Usage
```python
# API rate limiting
rate_limiter = RateLimiter(1000, 3600)  # 1000 requests per hour

@app.route('/api/data')
def get_data():
    client_id = get_client_id()
    current_time = time.time()
    
    if not rate_limiter.is_allowed(client_id, current_time):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    # Process request
    return jsonify({"data": get_data_from_db()})
```

### Monitoring and Debugging
```python
# Check current status
status = rate_limiter.get_customer_status("user_123", current_time)
print(f"Requests made: {status['requests_made']}/{rate_limiter.rate}")
print(f"Requests remaining: {status['requests_remaining']}")
print(f"Window ends at: {status['window_end']}")

# Cleanup old entries
removed = rate_limiter.cleanup_old_entries(current_time)
print(f"Cleaned up {removed} old entries")
```

## Assumptions and Design Decisions

### Assumptions Made

1. **Time Monotonicity**: Time generally moves forward (handles some backward movement gracefully)
2. **Customer Identification**: Customer IDs are unique strings
3. **Time Precision**: Unix timestamps (seconds since epoch) with floating point support
4. **Memory Constraints**: Reasonable number of active customers (not billions)
5. **Single Instance**: This implementation is for single-instance use (not distributed)

### Design Decisions

1. **Window Alignment**: Windows align to absolute time boundaries (not relative to first request)
2. **Floating Point Time**: Accepts float timestamps but converts to int for window calculations
3. **Automatic Cleanup**: Provides manual cleanup method rather than automatic background cleanup
4. **Stateful Design**: Maintains state in memory (not stateless)
5. **Synchronous API**: All operations are synchronous

### Edge Cases Handled

1. **Time Boundaries**: Exact window boundary transitions
2. **Floating Point Times**: Proper handling of fractional seconds
3. **Large Time Values**: Works with very large timestamps
4. **Multiple Customers**: Isolated rate limiting per customer
5. **Invalid Inputs**: Comprehensive input validation
6. **Time Rollbacks**: Graceful handling of time moving backward

## Testing Strategy

The test suite covers multiple dimensions:

### Test Categories

1. **Initialization Tests**: Parameter validation and setup
2. **Basic Functionality**: Core rate limiting logic
3. **Time Window Tests**: Window transitions and boundaries
4. **