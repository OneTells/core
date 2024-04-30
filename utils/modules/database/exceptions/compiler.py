from utils.modules.database.exceptions.database import DatabaseException


class CompilationError(DatabaseException):

    def __init__(self, query: str, *args, **kwargs) -> None:
        kwargs["message"] = f'При компиляции произошла ошибка. Объект компиляции: {query}'
        super().__init__(*args, **kwargs)
