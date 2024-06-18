from asyncpg import transaction, Connection
from asyncpg.pool import PoolAcquireContext


class Transaction:

    def __init__(self, pool_acquire_context: PoolAcquireContext) -> None:
        self.__pool_acquire_context = pool_acquire_context
        self.__transaction: transaction.Transaction | None = None

    async def __aenter__(self) -> Connection:
        connection = await self.__pool_acquire_context.__aenter__()

        self.__transaction = connection.transaction()
        await self.__transaction.__aenter__()

        return connection

    async def __aexit__(self, *exc) -> None:
        await self.__transaction.__aexit__(*exc)
        await self.__pool_acquire_context.__aexit__(*exc)
