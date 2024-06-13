from typing import Iterable

from utils.modules.requests.schemes.sessions import Response
from utils.modules.storage.objects import logger
from utils.modules.storage.schemes import File


class StorageError(Exception):

    def __init__(self, message: str, use_logger: bool = True):
        self.message = message

        if use_logger:
            logger.error(self.message)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.message}>'


class RequestError(StorageError):

    def __init__(self, response: Response | None):
        super().__init__(f'Ошибка при запросе. Ответ сервера: {response}', use_logger=False)
        self.response = response


class UploadError(StorageError):

    def __init__(self, path: str, response: Response | None):
        super().__init__(f'Ошибка при отправке файла в {path}. Ответ сервера: {response}')


class DeleteError(StorageError):

    def __init__(self, paths: Iterable[str], response: Response):
        super().__init__(f'Ошибка при удалении файлов: {paths}. Ответ сервера: {response}')


class GetFilesError(StorageError):

    def __init__(self, path: str, response: Response):
        super().__init__(f'Ошибка при получение файлов по указанному пути: {path}. Ответ сервера: {response}')


class WrongPathError(StorageError):

    def __init__(self, path: str):
        super().__init__(f'Путь указан неверно: {path}')


class EmptyFileError(StorageError):

    def __init__(self, file: File):
        super().__init__(f'Файл не может быть пустым. Файл: {file}')
