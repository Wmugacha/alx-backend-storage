#!/usr/bin/env python3

from typing import Callable, Optional, Union
from uuid import uuid4
import redis
import functools

'''
    Writing strings to Redis.
'''

def count_calls(method: Callable) -> Callable:
    '''
        Counts the number of times a methods of the Cache class are called.
    '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        '''
            Wrapper function.
        '''
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    '''
        Cache class.
    '''
    def __init__(self):
        '''
            Initialize the Redis Instance.
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    #@call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
            Generate key and Store input data.
        '''
        randomKey = str(uuid4())
        self._redis.set(randomKey, data)
        return randomKey

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''
            Get data from the cache.
        '''
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''
            Get a string from the cache.
        '''
        value = self._redis.get(key)
        return value.decode('utf-8')

    def get_int(self, key: str) -> int:
        '''
            Get an int from the cache.
        '''
        value = self._redis.get(key)
        try:
            value = int(value.decode('utf-8'))
        except Exception:
            value = 0
        return value







cache = Cache()

TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value