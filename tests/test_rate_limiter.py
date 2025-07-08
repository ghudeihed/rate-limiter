import pytest
import time 

from rate_limiter import RateLimiter

class TestRateLimiterInitialization:
    """Test rate limiter initialization and input validation"""
    
    def test_valid_initialization(self):
        """Test that rate limiter initializes correctly with valid parameters"""
        # Arrange
        limiter = RateLimiter(rate=5, time_window=10)
        
        # Assert
        assert limiter.rate == 5
        assert limiter.time_window == 10
        assert limiter.customers == {}
    
    def test_invalid_rate_parameters(self):
        """Test that invalid rate parameters raise ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate=0, time_window=10)
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate=-1, time_window=10)
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate="five", time_window=10)
            
    def test_invalid_time_window_parameters(self):
        """Test that invalid time window parameters raise ValueError"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window=0)
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window=-10)
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window="ten")
            
class TestRateLimiterBasicFunctionality:
    """Test basic rate limiting functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.rate_limiter = RateLimiter(5, 60)
    
    def test_first_request_allowed(self):
        """Test that the first request from a new customer is always allowed"""
        assert self.rate_limiter.is_allowed("user_123", 100) is True
        assert len(self.rate_limiter.customers) == 1
    
    def test_requests_within_rate_limit(self):
        """Test that requests within the rate limit are allowed"""
        customer_id = "user_123"
        base_time = 100
        
        # Make 5 requests (at the rate limit)
        for i in range(5):
            result = self.rate_limiter.is_allowed(customer_id, base_time + i)
            assert result is True, f"Request {i+1} should be allowed"
        
        # Verify the customer data is correct
        assert customer_id in self.rate_limiter.customers
        window_start, request_count = self.rate_limiter.customers[customer_id]
        assert request_count == 5
        assert window_start == 60  # (100 // 60) * 60
    
    def test_requests_exceeding_rate_limit(self):
        """Test that requests exceeding the rate limit are rejected within the same window"""
        customer_id = "user_123"
        base_time = 100  # Window = [60, 120)

        # Make 5 requests (at the rate limit)
        for i in range(5):
            assert self.rate_limiter.is_allowed(customer_id, base_time + i) is True

        # 6th request at time 110 — still within window
        assert self.rate_limiter.is_allowed(customer_id, base_time + 10) is False

        # 7th request at time 119 — still same window
        assert self.rate_limiter.is_allowed(customer_id, base_time + 19) is False

        # 8th request at time 120 — NEW window starts
        assert self.rate_limiter.is_allowed(customer_id, base_time + 20) is True

        # Verify state after rollover
        window_start, request_count = self.rate_limiter.customers[customer_id]
        assert window_start == 120 # (120 // 60) * 60
        assert request_count == 1
    
    def test_invalid_customer_id(self):
        """Test that invalid customer IDs raise ValueError"""
        # Arrange
        customer_id = None
        base_time = 100
        
        # Act & Assert
        with pytest.raises(ValueError, match="customer_id must be a non-empty string"):
            self.rate_limiter.is_allowed(customer_id, base_time)
        
        customer_id = ""
        with pytest.raises(ValueError, match="customer_id must be a non-empty string"):
            self.rate_limiter.is_allowed(customer_id, base_time)
        
        customer_id = 123
        with pytest.raises(ValueError, match="customer_id must be a non-empty string"):
            self.rate_limiter.is_allowed(customer_id, base_time)
    
    def test_invalid_current_time(self):
        """Test that invalid current time raises ValueError"""
        # Arrange
        customer_id = "user_123"
        current_time = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="current_time must be a non-negative integer"):
            self.rate_limiter.is_allowed(customer_id, current_time)
        
        current_time = -100
        with pytest.raises(ValueError, match="current_time must be a non-negative integer"):
            self.rate_limiter.is_allowed(customer_id, current_time)
        
        current_time = "100"
        with pytest.raises(ValueError, match="current_time must be a non-negative integer"):
            self.rate_limiter.is_allowed(customer_id, current_time)
            
class TestRateLimiterTimeWindows:
    """Test time window behavior and transitions"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.rate_limiter = RateLimiter(3, 30)  # 3 requests per 30 seconds
    
    def test_requests_within_same_window(self):
        """Test multiple requests within the same time window"""
        customer_id = "user_123"
        
        # First 3 requests should be allowed within window [60, 90)
        assert self.rate_limiter.is_allowed(customer_id, 60) is True   # Request 1
        assert self.rate_limiter.is_allowed(customer_id, 70) is True   # Request 2
        assert self.rate_limiter.is_allowed(customer_id, 80) is True   # Request 3
        
        # the 4th and 5th requests should be denied
        assert self.rate_limiter.is_allowed(customer_id, 85) is False  # Request 4 - rejected
        assert self.rate_limiter.is_allowed(customer_id, 89) is False  # Request 5 - rejected
    
    def test_requests_across_time_windows(self):
        """Test that rate limits reset when moving to a new time window"""
        customer_id = "user_123"
        
        # Fill up window [60, 90)
        assert self.rate_limiter.is_allowed(customer_id, 60) is True
        assert self.rate_limiter.is_allowed(customer_id, 70) is True
        assert self.rate_limiter.is_allowed(customer_id, 80) is True
        assert self.rate_limiter.is_allowed(customer_id, 85) is False  # Rejected (4th request within the same window)
        
        # Move to new window [90, 120)
        assert self.rate_limiter.is_allowed(customer_id, 90) is True   # New window, reset
        assert self.rate_limiter.is_allowed(customer_id, 100) is True
        assert self.rate_limiter.is_allowed(customer_id, 110) is True
        assert self.rate_limiter.is_allowed(customer_id, 115) is False  # Rejected again (4th request within the same window)
        
        # Check that the customer data is reset for the new window
        assert customer_id in self.rate_limiter.customers
        window_start, request_count = self.rate_limiter.customers[customer_id]
        assert request_count == 3
        assert window_start == 90  # (90 // 30) * 30
    
    def test_time_rollovers_and_resets(self):
        """Test various time rollover scenarios"""
        customer_id = "user_123"

        # First request
        assert self.rate_limiter.is_allowed(customer_id, 100) is True

        # Far future window (starts at 4980)
        assert self.rate_limiter.is_allowed(customer_id, 4980) is True
        assert self.rate_limiter.is_allowed(customer_id, 4990) is True
        assert self.rate_limiter.is_allowed(customer_id, 5000) is True

        # 4th request in the same window -> should be rejected
        assert self.rate_limiter.is_allowed(customer_id, 5005) is False

    def test_zero_time_handling(self):
        """Test handling of time zero and early timestamps"""
        customer_id = "user_123"
        
        # Window [0, 30)
        assert self.rate_limiter.is_allowed(customer_id, 0) is True
        assert self.rate_limiter.is_allowed(customer_id, 1) is True
        assert self.rate_limiter.is_allowed(customer_id, 29) is True
        assert self.rate_limiter.is_allowed(customer_id, 29) is False  # 4th request
