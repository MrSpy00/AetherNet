import time
import json
import random
import logging
from typing import Dict, Any, Optional, Tuple
import urllib.request
import urllib.error
import urllib.parse

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter per domain/key."""

    def __init__(self, requests_per_minute: int = 45):
        self.capacity = float(requests_per_minute)
        self.tokens = float(requests_per_minute)
        self.fill_rate = float(requests_per_minute) / 60.0  # tokens per sec
        self.last_update = time.time()

    def acquire(self) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class SimpleTTLCache:
    """In-memory dictionary cache with TTL in seconds."""

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            expires_at, value = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self.default_ttl
        self._cache[key] = (time.time() + duration, value)

    def clear(self) -> None:
        self._cache.clear()


class APIHttpClient:
    """Robust, Rate-Limited, Cached HTTP client with automatic Retries & Fallback."""

    def __init__(self, user_agent: str = "AetherNet-Hub/1.0", default_timeout: int = 8):
        self.user_agent = user_agent
        self.default_timeout = default_timeout
        self.cache = SimpleTTLCache(default_ttl=600)
        self.rate_limiters: Dict[str, RateLimiter] = {}

    def _get_rate_limiter(self, domain: str, requests_per_min: int = 45) -> RateLimiter:
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = RateLimiter(requests_per_min)
        return self.rate_limiters[domain]

    def get_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        cache_ttl: int = 600,
        rate_limit_pm: int = 60,
        max_retries: int = 2,
        timeout: Optional[int] = None
    ) -> Tuple[Optional[Dict[str, Any]], int, float]:
        """
        Performs HTTP GET request returning (json_data, status_code, latency_ms).
        Handles caching, rate limiting, and exponential retries.
        """
        if params:
            query_str = urllib.parse.urlencode(params)
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}{query_str}"
        else:
            full_url = url

        cache_key = f"GET:{full_url}"
        if use_cache:
            cached_val = self.cache.get(cache_key)
            if cached_val is not None:
                return cached_val, 200, 0.0

        parsed_domain = urllib.parse.urlparse(full_url).netloc
        limiter = self._get_rate_limiter(parsed_domain, rate_limit_pm)

        req_headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        if headers:
            req_headers.update(headers)

        effective_timeout = timeout or self.default_timeout
        attempt = 0
        last_status = 0
        
        while attempt <= max_retries:
            if not limiter.acquire() and attempt > 0:
                time.sleep(0.5)

            start_t = time.time()
            req = urllib.request.Request(full_url, headers=req_headers, method="GET")

            try:
                with urllib.request.urlopen(req, timeout=effective_timeout) as resp:
                    latency = (time.time() - start_t) * 1000.0
                    status_code = resp.getcode()
                    body = resp.read().decode("utf-8", errors="ignore")
                    
                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        data = {"raw": body}

                    if use_cache and status_code == 200:
                        self.cache.set(cache_key, data, ttl=cache_ttl)

                    return data, status_code, latency

            except urllib.error.HTTPError as e:
                latency = (time.time() - start_t) * 1000.0
                last_status = e.code
                if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                    sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    attempt += 1
                    continue
                else:
                    if e.code in (403, 404):
                        logger.debug(f"HTTPError {e.code} for {full_url}")
                    else:
                        logger.warning(f"HTTPError {e.code} for {full_url}")
                    return None, e.code, latency

            except Exception as e:
                latency = (time.time() - start_t) * 1000.0
                logger.debug(f"Request failed for {full_url}: {e}")
                if attempt < max_retries:
                    sleep_time = (2 ** attempt) + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    attempt += 1
                    continue
                return None, 0, latency

        return None, last_status, 0.0
