from typing import Self

from asyncpg import Pool, create_pool

from utils.modules.database.methods.connection import Connection
from utils.modules.database.methods.transaction import Transaction
from utils.modules.database.objects.logger import logger
from utils.modules.database.schemes.pool import DatabaseData


class DatabasePool:
    __pools: list[Self] = []

    def __init__(self, data: DatabaseData, *, pool_size: int = 5):
        self.__data = data
        self.__pool_size = pool_size

        self.__pool: Pool | None = None

    async def connect(self) -> None:
        self.__pool = await create_pool(
            self.__data.dsn,
            min_size=self.__pool_size,
            max_size=self.__pool_size,
            max_inactive_connection_lifetime=120,
            command_timeout=60
        )

        self.__pools.append(self)
        logger.debug(f'База данных {self.__data.name} подключена')

    async def close(self) -> None:
        await self.__pool.close()
        logger.debug(f'База данных {self.__data.name} отключена')

    def get_pool(self) -> Pool:
        return self.__pool

    def get_transaction(self) -> Transaction:
        return Transaction(self.__pool.acquire())

    def get_connection(self) -> Connection:
        return Connection(self.__pool.acquire())

    @classmethod
    async def close_all(cls) -> None:
        for pool in cls.__pools:
            await pool.close()
