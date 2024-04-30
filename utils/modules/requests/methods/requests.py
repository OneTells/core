from aiohttp import ClientTimeout

from utils.modules.requests.methods.sessions import Session
from utils.modules.requests.schemes.sessions import Response, Dict, Params


class Requests:
    __session: Session | None = None

    @classmethod
    def __create_session(cls):
        cls.__session = Session(timeout=ClientTimeout(total=60))

    @classmethod
    def __get_session(cls):
        if cls.__session is None:
            cls.__create_session()

        return cls.__session

    @classmethod
    async def get(cls, url: str, *, params: Params = None, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await cls.__get_session().get(url, params=params, headers=headers, cookies=cookies, **kwargs)

    @classmethod
    async def post(cls, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await cls.__get_session().post(url, headers=headers, cookies=cookies, **kwargs)

    @classmethod
    async def put(cls, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await cls.__get_session().put(url, headers=headers, cookies=cookies, **kwargs)

    @classmethod
    async def delete(cls, url: str, *, headers: Dict = None, cookies: Dict = None, **kwargs) -> Response:
        return await cls.__get_session().delete(url, headers=headers, cookies=cookies, **kwargs)
