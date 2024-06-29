from abc import abstractmethod, ABC

import orjson
from fastapi.responses import Response


class Coder[T](ABC):

    @classmethod
    @abstractmethod
    def dumps(cls, value: T) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def loads(cls, value: bytes) -> T:
        raise NotImplementedError


class ResponseCoder(Coder[Response]):

    @classmethod
    def dumps(cls, value: Response) -> bytes:
        obj = {
            'content': value.body,
            'media_type': value.media_type,
            'status_code': value.status_code,
            'raw_headers': value.headers.raw
        }

        return orjson.dumps(obj)

    @classmethod
    def loads(cls, value: bytes) -> Response:
        obj = orjson.loads(value)

        response = Response()

        response.body = obj['content']
        response.media_type = obj['media_type']
        response.raw_headers = obj['raw_headers']
        response.status_code = obj['status_code']

        return response
