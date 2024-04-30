import asyncio
from typing import Self

from aiohttp import ClientError, ServerDisconnectedError
from aiohttp.client import ClientSession

from utils.modules.requests.config.sessions import DEFAULT_USER_AGENT
from utils.modules.requests.schemes.sessions import Response, Methods, RequestArgs, Dict, Params


class Session:

    def __init__(self, **kwargs):
        self.__session = SessionPool.create(**kwargs)

    async def __request(self, method: Methods, url: str, depth: int = 0, **kwargs) -> Response:
        try:
            async with self.__session.request(method, url, **kwargs) as response:
                return Response(content=await response.read(), status_code=response.status, row_response=response)
        except (ServerDisconnectedError, ClientError, asyncio.TimeoutError):
            if depth == 2:
                return Response(content=None, status_code=500, row_response=None)

            return await self.__request(method, url, depth + 1, **kwargs)

    async def request(self, method: Methods, url: str, **kwargs) -> Response:
        args = RequestArgs(**kwargs)

        if args.headers is not None and args.headers.get('user-agent', None) is None:
            args.headers['user-agent'] = DEFAULT_USER_AGENT

        args.cookies = args.cookies or {}

        return await self.__request(method, url, **args.model_dump(by_alias=True))

    async def close(self) -> None:
        SessionPool.remove(self.__session)
        await self.__session.close()

    async def get(self, url: str, *, params: Params = None, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('GET', url, params=params, headers=headers, cookies=cookies, **kwargs)

    async def post(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('POST', url, headers=headers, cookies=cookies, **kwargs)

    async def put(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('PUT', url, headers=headers, cookies=cookies, **kwargs)

    async def delete(self, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await self.request('DELETE', url, headers=headers, cookies=cookies, **kwargs)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()


class SessionPool:
    __sessions: list[ClientSession] = []

    @classmethod
    def remove(cls, session: ClientSession):
        cls.__sessions.remove(session)

    @classmethod
    def create(cls, **kwargs) -> ClientSession:
        cls.__sessions.append(session := ClientSession(**kwargs))
        return session

    @classmethod
    async def close(cls):
        for session in cls.__sessions:
            await session.close()
