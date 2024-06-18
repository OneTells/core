from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.exc import CompileError
from sqlalchemy.sql.ddl import CreateTable

from utils.modules.database.exceptions.compiler import CompilationError
from utils.modules.database.objects.database import Base
from utils.modules.database.schemes.database import Query


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
