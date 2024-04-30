from multiprocessing.context import SpawnProcess

from utils.modules.logger.objects import logger
from utils.modules.worker.abstract.worker import BaseWorker
from utils.modules.worker.methods.trigger import Trigger
from utils.modules.worker.schemes.worker import WorkerData


class WorkerProcess:

    def __init__(self, worker: type[BaseWorker]) -> None:
        self.__worker = worker
        self.__process: SpawnProcess | None = None
        self.__logger = logger.bind(context=self.__worker.__name__)

    def start(self) -> None:
        self.__process = SpawnProcess(
            target=Trigger.run,
            args=(
                WorkerData(
                    worker_name=self.__worker.__name__, setting=self.__worker.setting(),
                    trigger=self.__worker.trigger(), executor=self.__worker.executor()
                ),
            ), name=f'Trigger_{self.__worker.__name__}'
        )
        self.__process.start()

        self.__logger.info('Запушен')

    def terminate(self):
        self.__process.terminate()
        self.__logger.debug('Отправлен запрос о завершении работы')

    def close(self):
        try:
            self.__process.join()
        except KeyboardInterrupt as error:
            self.__logger.error('Ошибка при закрытии')
            raise error

        self.__process.close()

        self.__logger.info('Остановлен')


class WorkerManager:

    def __init__(self, *workers: type[BaseWorker]):
        self.__workers = [WorkerProcess(worker) for worker in workers]

    def start(self):
        for worker in self.__workers:
            worker.start()

        logger.info('WorkerManager запушен')

    def close(self):
        for worker in self.__workers:
            worker.terminate()

        for worker in self.__workers:
            worker.close()

        logger.info('WorkerManager остановлен')
