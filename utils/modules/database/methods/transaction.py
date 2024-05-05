from asyncpg import transaction, Connection
from asyncpg.pool import PoolAcquireContext

from utils.modules.database.methods.pool import DatabasePool


class Transaction:

    def __init__(self) -> None:
        self.__pool_context: PoolAcquireContext | None = None
        self.__transaction: transaction.Transaction | None = None

    async def __aenter__(self) -> Connection:
        self.__pool_context = DatabasePool.get_pool().acquire()
        await self.__pool_context.__aenter__()

        self.__transaction = self.__pool_context.connection.transaction()
        await self.__transaction.__aenter__()

        return self.__pool_context.connection

    async def __aexit__(self, *exc) -> None:
        await self.__transaction.__aexit__(*exc)
        self.__transaction = None

        await self.__pool_context.__aexit__(*exc)
        self.__pool_context = None
