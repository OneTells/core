import asyncio
import time
from asyncio import CancelledError
from multiprocessing import Event, Value
from multiprocessing.context import SpawnProcess
from multiprocessing.managers import ValueProxy
from signal import signal, SIGTERM, SIGINT, SIG_IGN, default_int_handler
from typing import Any, AsyncIterator

from utils.modules.logger.objects import logger
from utils.modules.worker.schemes.executor import ExecutorData, ExecutorProcessData

try:
    from uvloop import new_event_loop
except ImportError:
    from asyncio import new_event_loop


class Executor:

    def __init__(self, executor_data: ExecutorData):
        self.__executor_data = executor_data
        self.__executor = executor_data.executor()

        self.__lifespan: AsyncIterator | None = None

        self.__logger = logger.bind(context=self.__executor_data.worker_name)

    async def __startup(self) -> None:
        await self.__executor.startup()

    async def __shutdown(self) -> None:
        await self.__executor.shutdown()

    def __get_final_args(self, args: Any) -> tuple[int | None, tuple]:
        if not isinstance(args, tuple):
            args = (args,)

        if self.__executor_data.limited_args is None:
            return None, args

        index = self.__executor_data.limited_args[2].get()
        unused_arg = self.__executor_data.limited_args[0][index]

        self.__executor_data.limited_args[1][index] = self.__executor_data.number

        return index, args + unused_arg

    async def __run(self):
        await self.__startup()
        self.__logger.debug('Исполнитель запушен')

        try:
            while True:
                if (args_in_queue := self.__executor_data.queue.get()) == 'Stop':
                    break

                index, args = self.__get_final_args(args_in_queue)

                self.__executor_data.set_start_work()

                self.__logger.debug(f'Выполняется исполнитель. Аргументы: {args}')

                try:
                    await self.__executor(*args)
                except Exception as error:
                    _ = error

                    self.__logger.exception(' ')
                    self.__logger.error(f'Ошибка при выполнении исполнителя. Аргументы: {args}')

                self.__executor_data.set_finish_work()

                if index is not None:
                    self.__executor_data.limited_args[1][index] = -1
                    self.__executor_data.limited_args[2].put(index)

                del args, args_in_queue, index
        except CancelledError:
            self.__logger.debug('Исполнитель принял запрос о завершении работы')

        await self.__shutdown()
        self.__logger.debug('Исполнитель завершён')

    @classmethod
    def run(cls, executor_data: ExecutorData) -> None:
        signal(SIGINT, SIG_IGN)
        signal(SIGTERM, default_int_handler)

        try:
            with asyncio.Runner(loop_factory=new_event_loop) as runner:
                runner.run(cls(executor_data).__run())
        except KeyboardInterrupt:
            pass


class ExecutorProcess:

    def __init__(self, data: ExecutorProcessData) -> None:
        self.__data = data

        self.__is_run_worker: Event | None = None
        self.__counter: ValueProxy[int] | None = None

        self.__process: SpawnProcess | None = None

        self.__current_time: float | None = None
        self.__current_counter: int | None = None

    def time(self):
        if self.__current_counter != self.__counter.value:
            self.__current_time = time.time()
            self.__current_counter = self.__counter.value

        return self.__current_time

    @property
    def is_working(self):
        return self.__is_run_worker.is_set()

    def start(self):
        self.__is_run_worker = Event()
        self.__counter = Value('l', 0)

        self.__process = SpawnProcess(
            target=Executor.run,
            args=(
                ExecutorData(
                    queue=self.__data.queue, is_run_worker=self.__is_run_worker,
                    worker_name=self.__data.worker_data.worker_name,
                    counter=self.__counter, limited_args=self.__data.limited_args,
                    executor=self.__data.worker_data.executor, number=self.__data.number
                ),
            ),
            name=f'Executor_{self.__data.number}_{self.__data.worker_data.worker_name}'
        )

        self.__process.start()

        self.__current_time = None
        self.__current_counter = None

    def is_alive(self) -> bool:
        return self.__process.is_alive()

    def terminate(self):
        self.__process.terminate()

    def close(self):
        self.__process.join()
        self.__process.close()
