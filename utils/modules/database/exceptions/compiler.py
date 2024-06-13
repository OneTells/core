from utils.modules.database.exceptions.database import DatabaseException


class CompilationError(DatabaseException):

    def __init__(self, query: str) -> None:
        super().__init__(f'При компиляции произошла ошибка. Объект компиляции: {query}')
