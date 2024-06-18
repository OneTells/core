from asyncpg import Connection as Connection_
from asyncpg.pool import PoolAcquireContext

from utils.modules.logger.objects import logger


class Connection:

    def __init__(self, pool_acquire_context: PoolAcquireContext) -> None:
        self.__pool_acquire_context = pool_acquire_context

    async def __aenter__(self) -> Connection_:
        return await self.__pool_acquire_context.__aenter__()

    async def __aexit__(self, *exc) -> None:
        logger.info(f'{exc}')
        await self.__pool_acquire_context.__aexit__(*exc)
