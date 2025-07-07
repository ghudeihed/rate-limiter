from datetime import datetime, date
from typing import Dict, Tuple

class RateLimiterFixedWindow:
    """Class that implements rate limiting with a fixed window algorithm."""

    def __init__(self, rate: int, time_window: int):
        """ Constructor that initializes the rate limiter with a specified rate and time window.

        Args:
            rate (int): maximum number of requests allowed per time window
            time_window (int): the time window in seconds over which to apply the rate limit
        Raises:
            ValueError: if rate or time_window is not a positive integer
        """
        pass
    
    def is_allowed(customer_id, current_time) -> bool: 
        """ Checks if a request is allowed for a given customer at the current time.

        Args:
            customer_id (str): unique identifier for the customer making the request
            current_time (datetime): the current timestamp in seconds since the epoch
        Returns:
            bool: true if the request is allowed, false if it should be rejected
        Raises:
            ValueError: if customer_id is not a string or current_time is not a datetime object
        """
        pass
