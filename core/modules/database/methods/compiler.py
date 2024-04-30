from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.exc import CompileError
from sqlalchemy.sql.ddl import CreateTable

from core.modules.database.objects.database import Base
from core.modules.database.schemes.database import Query
from core.modules.database.exceptions.compiler import CompilationError


class Compiler:

    @classmethod
    def compile_query(cls, query: Query) -> str:
        try:
            return query.compile(dialect=dialect(), compile_kwargs={"literal_binds": True}).string
        except CompileError as error:
            raise CompilationError(query) from error

    @classmethod
    def compile_table(cls, table: type[Base]) -> str:
        return CreateTable(Base.metadata.tables[table.__tablename__]).compile(dialect=dialect()).string
