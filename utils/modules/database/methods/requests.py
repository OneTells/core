from typing import overload, Callable

from asyncpg import Record, Connection
from sqlalchemy import Update as Update_, Select as Select_, Delete as Delete_
from sqlalchemy.dialects.postgresql import Insert as _Insert
from sqlalchemy.sql._typing import _ColumnsClauseArgument as Columns

from utils.modules.database.methods.database import Database
from utils.modules.database.schemes.database import T, Result


class Select(Select_):

    @overload
    async def fetch(self, *, model: type[T]) -> list[T]:
        ...

    @overload
    async def fetch(self, *, model: Callable[[Record], Result]) -> list[Result]:
        ...

    @overload
    async def fetch(self, *, model: None = None) -> list[Record]:
        ...

    async def fetch(self, *, model: type[T] | Callable[[Record], Result] = None) -> list[Record | Result | T]:
        return await Database.fetch(self, model=model)

    @overload
    async def fetch_one(self, *, model: type[T]) -> T | None:
        ...

    @overload
    async def fetch_one(self, *, model: Callable[[Record], Result]) -> Result | None:
        ...

    @overload
    async def fetch_one(self, *, model: None = None) -> Record | None:
        ...

    async def fetch_one(self, *, model: type[T] | Callable[[Record], Result] = None) -> Record | Result | T | None:
        return await Database.fetch_one(self, model=model)


class Update(Update_):

    async def execute(self, connection: Connection = None) -> None:
        await Database.execute(self, connection=connection)


class Insert(_Insert):

    async def execute(self, connection: Connection = None) -> None:
        await Database.execute(self, connection=connection)

    @overload
    async def returning(self, *cols: Columns, model: type[T], connection: Connection = None) -> T | None:
        ...

    @overload
    async def returning(self, *cols: Columns, model: Callable[[Record], Result], connection: Connection = None) -> Result | None:
        ...

    @overload
    async def returning(self, *cols: Columns, model: None = None, connection: Connection = None) -> Record | None:
        ...

    async def returning(
        self,
        *cols: Columns,
        model: type[T] | Callable[[Record], Result] = None,
        connection: Connection = None
    ) -> Record | Result | T | None:
        return await Database.fetch_one(super().returning(*cols), model=model, connection=connection)


class Delete(Delete_):

    async def execute(self, connection: Connection = None) -> None:
        await Database.execute(self, connection=connection)
