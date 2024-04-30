from abc import ABC, abstractmethod


class Lifespan(ABC):

    @abstractmethod
    async def startup(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        raise NotImplementedError
