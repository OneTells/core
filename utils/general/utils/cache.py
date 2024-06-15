from functools import lru_cache, wraps
from time import perf_counter
from typing import Callable

from utils.general.utils.timer import timer


class CacheWithTimer:

    def __init__(self, *, hours: int = 0, minutes: int = 0, seconds: int = 0, maxsize: int = 128):
        self.__delta = timer(hours=hours, minutes=minutes, seconds=seconds)
        self.__maxsize = maxsize

        self.__expiration: float | None = None
        self.__function = None

    def __cache_clear(self) -> None:
        if perf_counter() < self.__expiration:
            return

        self.__function.cache_clear()
        self.__expiration = perf_counter() + self.__delta

    def __call__(self, function: Callable):
        self.__function = lru_cache(maxsize=self.__maxsize)(function)
        self.__expiration = perf_counter() + self.__delta

        @wraps(function)
        def wrapper(*args, **kwargs):
            self.__cache_clear()
            return self.__function(*args, **kwargs)

        return wrapper
