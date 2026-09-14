"""
Rate limiting to prevent API abuse
Implements token bucket algorithm
"""

import time
from typing import Dict, Optional
from config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class RateLimiter:
    """
    Token bucket rate limiter
    Allows N requests per time window
    """
    
    def __init__(
        self,
        requests_per_second: int = RATE_LIMIT_REQUESTS,
        window_seconds: int = RATE_LIMIT_WINDOW
    ):
        """
        Initialize rate limiter
        
        Args:
            requests_per_second: Number of allowed requests per second
            window_seconds: Time window in seconds (usually 1)
        """
        self.requests_per_second = requests_per_second
        self.window_seconds = window_seconds
        
        # Track tokens per user
        self.buckets: Dict[str, dict] = {}
    
    def _get_bucket(self, user_id: str) -> dict:
        """Get or create token bucket for user"""
        if user_id not in self.buckets:
            self.buckets[user_id] = {
                'tokens': float(self.requests_per_second),
                'last_updated': time.time()
            }
        return self.buckets[user_id]
    
    def _refill_bucket(self, bucket: dict, current_time: float):
        """Refill bucket based on elapsed time"""
        elapsed = current_time - bucket['last_updated']
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * (self.requests_per_second / self.window_seconds)
        bucket['tokens'] = min(
            float(self.requests_per_second),
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_updated'] = current_time
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has tokens available
        
        Args:
            user_id: User identifier
            
        Returns:
            True if request allowed, False if rate limited
        """
        bucket = self._get_bucket(user_id)
        current_time = time.time()
        
        # Refill bucket
        self._refill_bucket(bucket, current_time)
        
        # Check if tokens available
        if bucket['tokens'] >= 1.0:
            bucket['tokens'] -= 1.0
            return True
        
        return False
    
    def allow_request(self, user_id: str) -> None:
        """
        Allow request or raise RateLimitError
        
        Args:
            user_id: User identifier
            
        Raises:
            RateLimitError: If rate limit exceeded
        """
        if not self.check_rate_limit(user_id):
            raise RateLimitError(
                f"Rate limit exceeded for user {user_id}. "
                f"Max {self.requests_per_second} requests per {self.window_seconds}s"
            )
    
    def get_remaining_tokens(self, user_id: str) -> float:
        """
        Get remaining tokens for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of remaining tokens
        """
        bucket = self._get_bucket(user_id)
        current_time = time.time()
        self._refill_bucket(bucket, current_time)
        return max(0, bucket['tokens'])
    
    def reset_user(self, user_id: str) -> None:
        """Reset rate limit for user"""
        if user_id in self.buckets:
            del self.buckets[user_id]
    
    def reset_all(self) -> None:
        """Reset all rate limits"""
        self.buckets.clear()


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def check_rate_limit(user_id: str = "default") -> bool:
    """Check rate limit for user"""
    return get_rate_limiter().check_rate_limit(user_id)


def allow_request(user_id: str = "default") -> None:
    """Allow request or raise RateLimitError"""
    get_rate_limiter().allow_request(user_id)
