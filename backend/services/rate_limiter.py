import os
import time
import threading
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class InMemoryRateLimiter:
    """
    Lightweight, thread-safe in-memory sliding-window rate limiter.
    Designed for development and local deployment without external infrastructure dependencies.
    """
    _instance: Optional['InMemoryRateLimiter'] = None

    def __init__(
        self,
        default_max_requests: int = 60,
        default_window_seconds: int = 60,
        enabled: bool = True
    ):
        self.lock = threading.Lock()
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.max_requests = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", default_max_requests))
        self.window_seconds = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", default_window_seconds))
        env_enabled = os.environ.get("RATE_LIMIT_ENABLED", str(enabled)).lower()
        self.enabled = env_enabled in ("true", "1", "yes")

    @classmethod
    def get_instance(cls) -> 'InMemoryRateLimiter':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def check(self, client_ip: str, endpoint: str = "default") -> Tuple[bool, int]:
        """
        Checks if the client request is permitted under the current rate limit.
        Returns:
            (allowed: bool, retry_after_seconds: int)
        """
        if not self.enabled:
            return True, 0

        # Disregard empty IP
        ip_key = f"{client_ip}:{endpoint}" if client_ip else f"unknown:{endpoint}"
        now = time.monotonic()

        with self.lock:
            timestamps = self.requests[ip_key]
            # Prune timestamps older than window
            cutoff = now - self.window_seconds
            valid_timestamps = [t for t in timestamps if t > cutoff]

            if len(valid_timestamps) >= self.max_requests:
                # Calculate retry-after seconds
                oldest = valid_timestamps[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest)))
                self.requests[ip_key] = valid_timestamps
                return False, retry_after

            # Record this request
            valid_timestamps.append(now)
            self.requests[ip_key] = valid_timestamps
            return True, 0

    def reset(self):
        """
        Clears all recorded rate limit tracking data. Useful for test suites.
        """
        with self.lock:
            self.requests.clear()

    def set_limits(self, max_requests: int, window_seconds: int):
        """
        Dynamically updates rate limits. Useful for targeted rate limit testing.
        """
        with self.lock:
            self.max_requests = max_requests
            self.window_seconds = window_seconds


rate_limiter = InMemoryRateLimiter.get_instance()
