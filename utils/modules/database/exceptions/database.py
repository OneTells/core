from utils.modules.database.objects.logger import logger


class DatabaseException(Exception):

    def __init__(self, message: str = None) -> None:
        self.message = message or 'Ошибка при работе с database'
        logger.error(self.message)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.message}>'


class ExecuteError(DatabaseException):

    def __init__(self, compiled_query: str) -> None:
        super().__init__(f'Слишком много попыток выполнить запрос. Запрос: {compiled_query}')


class TooManyRecords(DatabaseException):

    def __init__(self, compiled_query: str) -> None:
        super().__init__(f'Запрос вернул несколько записей. Запрос: {compiled_query}')
