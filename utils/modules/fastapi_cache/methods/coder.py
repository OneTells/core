import base64
from abc import abstractmethod, ABC

import orjson
from fastapi.responses import Response


class Coder[T](ABC):

    @classmethod
    @abstractmethod
    def encode(cls, value: T) -> bytes:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def decode(cls, value: bytes) -> T:
        raise NotImplementedError


class ResponseCoder(Coder[Response]):

    @classmethod
    def encode(cls, value: Response) -> bytes:
        obj = {
            'content': base64.b64encode(value.body).decode(),
            'media_type': value.media_type,
            'status_code': value.status_code
        }

        return orjson.dumps(obj)

    @classmethod
    def decode(cls, value: bytes) -> Response:
        obj = orjson.loads(value)

        response = Response()

        response.body = base64.b64decode(obj['content'].encode())
        response.media_type = obj['media_type']
        response.status_code = obj['status_code']

        return response
