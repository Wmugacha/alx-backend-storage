#!/usr/bin/env python3
""" Redis Module for web page caching and access counting. """

import functools
import redis
import requests
from typing import Callable

_redis = redis.Redis()


def cache_and_count(func: Callable) -> Callable:
    """
    Decorator: Caches function output for 10s and tracks URL access count.
    """
    @functools.wraps(func)
    def wrapper(url: str, *args, **kwargs) -> str:
        """Wrapper function for caching and counting logic."""
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"

        # Try to retrieve from cache.
        cached_html = _redis.get(cache_key)
        if cached_html:
            return cached_html.decode('utf-8')

        # If not cached, call original function.
        result = func(url, *args, **kwargs)

        # Cache the result with 10-second expiration.
        _redis.setex(cache_key, 10, result)

        # Increment access count.
        _redis.incr(count_key)

        return result
    return wrapper


@cache_and_count
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a given URL using requests.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk/"

    print(f"Fetching: {test_url}")
    page_content = get_page(test_url)
    print(f"Content snippet: {page_content[:100]}...")

    count = _redis.get(f"count:{test_url}")
    print(f"Access count: {count.decode() if count else '0'}")

    print("\nFetching again (should be from cache):")
    get_page(test_url)
    count = _redis.get(f"count:{test_url}")
    print(f"Access count: {count.decode() if count else '0'}")
