import time
from abc import ABC, abstractmethod


class Storage(ABC):

    @classmethod
    @abstractmethod
    async def get(cls, key: str) -> tuple[int, bytes] | None:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def set(cls, key: str, value: bytes, expire: int | None = 0) -> None:
        raise NotImplementedError


class MemoryStorage(Storage):
    __storage: dict[str, tuple[bytes, int]] = {}

    @classmethod
    async def get(cls, key: str) -> tuple[int, bytes] | None:
        value = cls.__storage.get(key)

        if not value:
            return

        if (ttl := value[1] - int(time.time())) >= 0:
            return ttl, value[2]

        del cls.__storage[key]

    @classmethod
    async def set(cls, key: str, value: bytes, expire: int | None = 0) -> None:
        cls.__storage[key] = (value, int(time.time()) + expire)