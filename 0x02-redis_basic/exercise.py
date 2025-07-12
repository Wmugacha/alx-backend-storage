#!/usr/bin/env python3

from typing import Callable, Optional, Union
from uuid import uuid4
import redis
import functools

'''
    Writing strings to Redis.
'''


def call_history(method: Callable) -> Callable:
    """ Decorator to store the history of inputs and
    outputs for a particular function.
    """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """ Wrapper for decorator functionality """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data

    return wrapper


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
    @call_history
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


def replay(method: Callable) -> None:
    """
    Replays the history of a function
    Args:
        method: The function to be decorated
    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name).decode("utf-8")
    print(f"{name} was called {calls} times:")
    inputs = cache.lrange(name + ":inputs", 0, -1)
    outputs = cache.lrange(name + ":outputs", 0, -1)
    for i, o in zip(inputs, outputs):
        print(f"{name}(*{i.decode('utf-8')}) -> {o.decode('utf-8')}")


# Test case for number 1
cache = Cache()

TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value

# Test cases for Replay function
cache.store("foo")
cache.store("bar")
cache.store(42)
replay(cache.store)
