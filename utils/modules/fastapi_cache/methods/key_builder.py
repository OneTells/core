import hashlib
from abc import abstractmethod, ABC
from typing import Callable, Any


class KeyBuilder(ABC):

    @classmethod
    @abstractmethod
    def build[** P](cls, func: Callable[P, Any], kwargs: P) -> str:
        raise NotImplementedError


class DefaultKeyBuilder(KeyBuilder):

    @classmethod
    @abstractmethod
    def build[** P](cls, func: Callable[P, Any], kwargs: P) -> str:
        return hashlib.md5(f"{func.__module__}:{func.__name__}:{kwargs}".encode()).hexdigest()
