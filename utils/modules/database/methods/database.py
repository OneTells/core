from asyncio import sleep
from inspect import isclass
from typing import Callable as Call

from asyncpg import Record as Rec, ConnectionDoesNotExistError, CannotConnectNowError, Connection, Pool
from pydantic import BaseModel

from utils.modules.database.exceptions.database import ExecuteError, TooManyRecords
from utils.modules.database.methods.compiler import Compiler
from utils.modules.database.methods.pool import DatabasePool
from utils.modules.database.schemes.database import Query, T, Result as Res


class Database:

    @classmethod
    async def __fetch(cls, compiled_query: str, connection: Connection | Pool, depth: int = 0) -> list[Rec]:
        try:
            return await connection.fetch(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError) as error:
            if depth == 3:
                raise ExecuteError(compiled_query) from error

            await sleep(2)
            return await cls.__fetch(compiled_query, connection, depth + 1)

    @classmethod
    async def __execute(cls, compiled_query: str, connection: Connection | Pool, depth: int = 0) -> None:
        try:
            await connection.execute(compiled_query)
        except (CannotConnectNowError, ConnectionDoesNotExistError, ConnectionRefusedError) as error:
            if depth == 3:
                raise ExecuteError(compiled_query) from error

            await sleep(2)
            return await cls.__execute(compiled_query, connection, depth + 1)

    @classmethod
    async def fetch(
        cls,
        query: Query,
        connection: Connection | DatabasePool,
        *,
        model: type[T] | Call[[Rec], Res] = None
    ) -> list[Rec | Res | T]:
        if isinstance(connection, DatabasePool):
            connection = connection.get_pool()

        result = await cls.__fetch(Compiler.compile_query(query), connection)

        if model is None:
            return result

        if isclass(model) and issubclass(model, BaseModel):
            return list(map(lambda record: model(**record), result))

        return list(map(model, result))

    @classmethod
    async def fetch_one(
        cls,
        query: Query,
        connection: Connection | DatabasePool,
        *,
        model: type[T] | Call[[Rec], Res] = None
    ) -> Rec | Res | T | None:
        if isinstance(connection, DatabasePool):
            connection = connection.get_pool()

        result = await cls.__fetch(compiled_query := Compiler.compile_query(query), connection)

        if len(result) == 0:
            return None

        if len(result) > 1:
            raise TooManyRecords(compiled_query)

        if model is None:
            return result[0]

        if isclass(model) and issubclass(model, BaseModel):
            return model(**result[0])

        return model(result[0])

    @classmethod
    async def execute(cls, query: Query, connection: Connection | DatabasePool) -> None:
        if isinstance(connection, DatabasePool):
            connection = connection.get_pool()

        await cls.__execute(Compiler.compile_query(query), connection)
