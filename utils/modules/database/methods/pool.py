from asyncpg import Pool, create_pool

from utils.modules.database.objects.logger import logger
from utils.modules.database.schemes.pool import DatabaseData


class DatabasePool:
    __pool: Pool

    @classmethod
    def get_pool(cls) -> Pool:
        return cls.__pool

    @classmethod
    async def connect(cls, data: DatabaseData, *, pool_size: int = 5) -> None:
        cls.__pool = await create_pool(
            data.dsn,
            min_size=pool_size,
            max_size=pool_size,
            max_inactive_connection_lifetime=120,
            command_timeout=60
        )

        logger.debug(f'База данных подключена')

    @classmethod
    async def disconnect(cls) -> None:
        await cls.__pool.close()
        logger.debug('База данных отключена')
