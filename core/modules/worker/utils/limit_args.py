from functools import reduce
from itertools import repeat
from typing import Any


class LimitArgs:

    def __init__(self, *args: Any, times: int = 1):
        self.__args = reduce(
            lambda x, y: x + y, repeat(list(map(lambda x: x if isinstance(x, tuple) else (x,), args)), times=times)
        )

    def unpack(self) -> tuple[tuple[Any], ...]:
        return tuple(self.__args)
