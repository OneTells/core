from abc import abstractmethod, ABC

from utils.modules.worker.abstract.lifespan import Lifespan


class BaseTrigger(Lifespan, ABC):

    @abstractmethod
    async def __call__(self) -> list | None:
        raise NotImplementedError
