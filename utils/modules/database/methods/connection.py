from asyncpg import Connection as Connection_

from utils.modules.database.methods.pool import DatabasePool


class Connection:

    def __init__(self) -> None:
        self.__pool_context = DatabasePool.get_pool().acquire()

    async def __aenter__(self) -> Connection_:
        return await self.__pool_context.__aenter__()

    async def __aexit__(self, *exc) -> None:
        await self.__pool_context.__aexit__(*exc)
