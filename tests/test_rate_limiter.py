import pytest
import time 

from rate_limiter import RateLimiter

class TestRateLimiterInitialization:
    def test_valid_initialization(self):
        # Arrange
        limiter = RateLimiter(rate=5, time_window=10)
        
        # Assert
        assert limiter.rate == 5
        assert limiter.time_window == 10
        assert limiter.customers == {}
    
    def test_invalid_initialization_rate(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate=0, time_window=10)
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate=-1, time_window=10)
        with pytest.raises(ValueError, match="Rate must be a positive integer"):
            RateLimiter(rate="five", time_window=10)
            
    def test_invalid_time_window(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window=0)
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window=-10)
        with pytest.raises(ValueError, match="Time window must be a positive integer"):
            RateLimiter(rate=5, time_window="ten")