from dataclasses import dataclass

from utils.modules.worker.abstract.executor import BaseExecutor
from utils.modules.worker.abstract.trigger import BaseTrigger
from utils.modules.worker.schemes.setting import Setting


@dataclass(slots=True, frozen=True)
class WorkerData:
    worker_name: str
    setting: Setting

    trigger: type[BaseTrigger]
    executor: type[BaseExecutor] | None
