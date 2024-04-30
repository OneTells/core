from abc import ABC, abstractmethod

from utils.modules.worker.abstract.executor import BaseExecutor
from utils.modules.worker.abstract.trigger import BaseTrigger
from utils.modules.worker.schemes.setting import Setting


class BaseWorker(ABC):

    @staticmethod
    @abstractmethod
    def setting() -> Setting:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def executor() -> type[BaseExecutor] | None:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def trigger() -> type[BaseTrigger]:
        raise NotImplementedError
