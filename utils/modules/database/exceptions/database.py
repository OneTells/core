from utils.modules.database.objects.logger import logger


class DatabaseException(Exception):

    def __init__(self, *args, **kwargs) -> None:
        self.message = kwargs.get('message', None) or 'Ошибка при работе с database'

        if kwargs.get('use_logger', True):
            logger.error(self.message)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.message}>'


class ExecuteError(DatabaseException):

    def __init__(self, compiled_query: str, *args, **kwargs) -> None:
        kwargs["message"] = f'Слишком много попыток выполнить запрос. Запрос: {compiled_query}'
        super().__init__(*args, **kwargs)


class TooManyRecords(DatabaseException):

    def __init__(self, compiled_query: str, *args, **kwargs) -> None:
        kwargs["message"] = f'Запрос вернул несколько записей. Запрос: {compiled_query}'
        super().__init__(*args, **kwargs)
