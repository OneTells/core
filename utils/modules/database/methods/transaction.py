from asyncpg import transaction, Connection as Connection_

from utils.modules.database.methods.connection import Connection


class Transaction:

    def __init__(self) -> None:
        self.__connection = Connection()
        self.__transaction: transaction.Transaction | None = None

    async def __aenter__(self) -> Connection_:
        connection = await self.__connection.__aenter__()

        self.__transaction = connection.transaction()
        await self.__transaction.__aenter__()

        return connection

    async def __aexit__(self, *exc) -> None:
        await self.__transaction.__aexit__(*exc)
        await self.__connection.__aexit__(*exc)
