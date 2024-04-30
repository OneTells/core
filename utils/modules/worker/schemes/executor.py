from array import ArrayType
from dataclasses import dataclass
from multiprocessing import Queue
from multiprocessing.managers import ValueProxy
from multiprocessing.synchronize import Event

from utils.modules.worker.abstract.executor import BaseExecutor
from utils.modules.worker.schemes.worker import WorkerData


@dataclass(slots=True, frozen=True)
class ExecutorProcessData:
    number: int

    limited_args: tuple[list[tuple], ArrayType, Queue] | None
    queue: Queue

    worker_data: WorkerData


@dataclass(slots=True, frozen=True)
class ExecutorData:
    worker_name: str

    executor: type[BaseExecutor]

    queue: Queue

    is_run_worker: Event
    counter: ValueProxy[int]

    limited_args: tuple[list[tuple], ArrayType, Queue] | None

    number: int

    def set_start_work(self):
        self.is_run_worker.set()

    def set_finish_work(self):
        self.is_run_worker.clear()
        self.counter.value += 1
