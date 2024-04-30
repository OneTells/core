from abc import ABC, abstractmethod

from core.modules.worker.abstract.lifespan import Lifespan


class BaseExecutor(Lifespan, ABC):

    @abstractmethod
    async def __call__(self, *args) -> None:
        raise NotImplementedError
