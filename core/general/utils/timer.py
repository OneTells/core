from time import perf_counter_ns
from typing import Callable, Any

from core.modules.database.objects.logger import logger


def timer(*, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> float:
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def benchmark(title: str, args_function: Callable[[tuple], Any] = lambda x: x[1:]):
    def decorator(function: Callable):
        async def wrapper(*args, **kwargs):
            start = perf_counter_ns()
            result = await function(*args, **kwargs)
            logger.info(f'{title} {args_function(args)} | {(perf_counter_ns() - start) / 1_000_000:.2f} мс')

            return result

        return wrapper

    return decorator
