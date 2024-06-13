from asyncio import iscoroutinefunction
from time import perf_counter_ns
from typing import Callable

from utils.modules.logger.objects import logger


def timer(*, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> float:
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


class Benchmark:

    def __init__(self, title: str):
        self.__title = title

    def __logging(self, delta: int, *args, **kwargs):
        logger.info(f'{self.__title.format(**kwargs, args=args)} | {delta / 1_000_000:.2f} мс')

    def __call__(self, function: Callable):
        async def async_wrapper(*args, **kwargs):
            start = perf_counter_ns()
            result = await function(*args, **kwargs)
            self.__logging(perf_counter_ns() - start, *args, **kwargs)
            return result

        def wrapper(*args, **kwargs):
            start = perf_counter_ns()
            result = function(*args, **kwargs)
            self.__logging(perf_counter_ns() - start, *args, **kwargs)
            return result

        return async_wrapper if iscoroutinefunction(function) else wrapper
