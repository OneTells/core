from dataclasses import dataclass

from core.modules.worker.abstract.executor import BaseExecutor
from core.modules.worker.abstract.trigger import BaseTrigger
from core.modules.worker.schemes.setting import Setting


@dataclass(slots=True, frozen=True)
class WorkerData:
    worker_name: str
    setting: Setting

    trigger: type[BaseTrigger]
    executor: type[BaseExecutor] | None
