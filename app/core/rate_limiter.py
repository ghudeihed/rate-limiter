import threading
from collections import defaultdict
from typing import Dict, Tuple, Union

class RateLimiter:
    """Class that implements rate limiting with a fixed window algorithm."""

    def __init__(self, rate: int, time_window: int):
        """ Constructor that initializes the rate limiter with a specified rate and time window.

        Args:
            rate (int): maximum number of requests allowed per time window
            time_window (int): the time window in seconds over which to apply the rate limit
        Raises:
            ValueError: if rate or time_window is not a positive integer
        """
        if not isinstance(rate, int) or rate <= 0:
            raise ValueError("Rate must be a positive integer")
        if not isinstance(time_window, int) or time_window <= 0:
            raise ValueError("Time window must be a positive integer")
        
        self.rate = rate
        self.time_window = time_window
        
        # Dictionary to store customer data: customer_id -> (window_start, request_count)
        self.customers: Dict[str, Tuple[int, int]] = {}
        
        # Per-customer locks for fine-grained concurrency
        self._customer_locks = defaultdict(threading.Lock)
        self._locks_lock = threading.Lock()  # Protects the locks dict
    
    def is_allowed(self, customer_id: str, current_time: Union[int, float]) -> bool:
        """ Checks if a request is allowed for a given customer at the current time.

        Args:
            customer_id (str): unique identifier for the customer making the request
            current_time (int | float): the current timestamp in seconds since the epoch
        Returns:
            bool: true if the request is allowed, false if it should be rejected
        Raises:
            ValueError: If customer_id is invalid or current_time is negative.
        """
        if not customer_id or not isinstance(customer_id, str):
            raise ValueError("customer_id must be a non-empty string")
        if not isinstance(current_time, (int, float)) or current_time < 0:
            raise ValueError("current_time must be a non-negative number")

        current_time_int = int(current_time)
        current_window_start = (current_time_int // self.time_window) * self.time_window

        # Get or create lock for this customer
        with self._locks_lock:
            customer_lock = self._customer_locks[customer_id]
        
        # Now process this customer atomically
        with customer_lock:   
            # Check if customer exists in our tracking
            if customer_id not in self.customers:
                # New customer - initialize with current window and first request
                self.customers[customer_id] = (current_window_start, 1)
                return True 
            
            # Get customer's current window data
            window_start, request_count = self.customers[customer_id]
            
            # Check if we're in a new window
            if current_window_start > window_start:
                # New window has started, reset request count
                self.customers[customer_id] = (current_window_start, 1)
                return True
            
            # Same window - check request count
            if request_count >= self.rate:
                # Rate limit exceeded
                return False
            
            # Within rate limit, increment request count
            self.customers[customer_id] = (window_start, request_count + 1)
            return True
        
# Example usage and testing
if __name__ == "__main__":
    # Create a rate limiter: 5 requests per 60 seconds
    rate_limiter = RateLimiter(5, 60)
    
    print("=== Fixed Window Rate Limiter Example ===")
    print("Rate: 5 requests per 60 seconds")
    print()
    
    # Test the example from the requirements
    test_times = [100, 110, 115, 120, 125, 130, 170]
    customer_id = "user_123"
    
    for i, test_time in enumerate(test_times):
        allowed = rate_limiter.is_allowed(customer_id, test_time) 
        
        print(f"Request {i+1} at time {test_time}:")
        print(f"  Allowed: {allowed}") 
        print()
    
    # Test with multiple customers
    print("=== Multiple Customers Test ===")
    rate_limiter2 = RateLimiter(3, 30)  # 3 requests per 30 seconds
    
    customers = ["alice", "bob", "charlie"]
    base_time = 200
    
    for i in range(5):
        for customer in customers:
            allowed = rate_limiter2.is_allowed(customer, base_time + i)
            print(f"Time {base_time + i}, {customer}: {'Allowed' if allowed else 'Denied'}")