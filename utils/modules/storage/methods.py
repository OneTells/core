import asyncio
import hmac
from asyncio import sleep
from base64 import b64encode
from datetime import datetime, UTC
from hashlib import sha256, md5
from typing import Iterable
from urllib.parse import quote, unquote
from xml.etree import ElementTree

from aiohttp import ClientSession, ClientError, ClientTimeout

from utils.modules.requests.schemes.sessions import Methods, Response
from utils.modules.storage.exceptions import RequestError, UploadError, DeleteError, GetFilesError, WrongPathError, EmptyFileError
from utils.modules.storage.schemes import AuthorizationData, StorageData, File


class _Authorization:

    def __init__(self, data: AuthorizationData):
        self.__data = data

        self.__date = data.datatime.strftime("%Y%m%d")
        self.__timestamp = data.datatime.strftime("%Y%m%dT%H%M%SZ")

        self.__headers = data.headers | {'host': data.storage_data.host}
        self.__params = sorted(data.params.items(), key=lambda x: x[0].lower())

        sorted_headers = sorted(self.__headers.items(), key=lambda x: x[0].lower())
        self.__signed_headers = ';'.join(map(lambda x: x[0].lower(), sorted_headers))
        self.__canonical_headers = '\n'.join(f'{k.lower()}:{v.strip()}' for k, v in sorted_headers)

    def __get_signing_key(self) -> bytes:
        date_key = hmac.new(f"AWS4{self.__data.storage_data.secret_key}".encode(), self.__date.encode(), sha256).digest()
        date_region_key = hmac.new(date_key, self.__data.storage_data.region.encode(), sha256).digest()
        date_region_service_key = hmac.new(date_region_key, self.__data.storage_data.service.encode(), sha256).digest()

        return hmac.new(date_region_service_key, "aws4_request".encode(), sha256).digest()

    def __get_canonical_request(self) -> str:
        canonical_query = '&'.join(f'{k.lower()}={v.strip()}' for k, v in self.__params)
        hashed_payload = self.__headers['X-Amz-Content-SHA256']

        return (
            f"{self.__data.method}\n{self.__data.canonical_uri}\n{canonical_query}\n"
            f"{self.__canonical_headers}\n\n{self.__signed_headers}\n{hashed_payload}"
        )

    def __get_string_to_sign(self) -> str:
        canonical_request = self.__get_canonical_request()
        scope = f'{self.__date}/{self.__data.storage_data.region}/{self.__data.storage_data.service}/aws4_request'

        return f'AWS4-HMAC-SHA256\n{self.__timestamp}\n{scope}\n{sha256(canonical_request.encode()).hexdigest()}'

    def __get_signature(self) -> str:
        signing_key = self.__get_signing_key()
        string_to_sign = self.__get_string_to_sign()

        return hmac.new(signing_key, string_to_sign.encode(), sha256).hexdigest()

    def get_key(self):
        credential = (
            f'{self.__data.storage_data.access_key}/{self.__date}/'
            f'{self.__data.storage_data.region}/{self.__data.storage_data.service}/aws4_request'
        )
        signature = self.__get_signature()

        return f'AWS4-HMAC-SHA256 Credential={credential}, SignedHeaders={self.__signed_headers}, Signature={signature}'


class Storage:

    def __init__(self, data: StorageData):
        self.__data = data
        self.__session: ClientSession = ClientSession(timeout=ClientTimeout(total=60))

    async def __request(self, method: Methods, url: str, headers: dict[str, str], data: bytes = None, depth: int = 0) -> Response:
        try:
            async with self.__session.request(method, url, headers=headers, data=data) as response:
                response = Response(content=await response.read(), status_code=response.status)
        except (ClientError, asyncio.TimeoutError):
            response = None

        if response is not None and response.status_code == 200:
            if method == 'PUT' and len(response.content) != 0:
                raise RequestError(response)

            return response

        if depth >= 3:
            raise RequestError(response)

        await sleep(1)
        return await self.__request(method, url, headers, data, depth + 1)

    async def __upload_file(self, base_path: str, file: File) -> None:
        datetime_ = datetime.now(UTC)
        canonical_uri = f'/{self.__data.bucket_name}/{base_path}/{file.name}'

        headers = {
            'Content-Type': file.type.value,
            'Content-MD5': b64encode(md5(file.content).digest()).decode('ascii'),
            'X-Amz-Date': datetime_.strftime('%Y%m%dT%H%M%SZ'),
            'X-Amz-Content-SHA256': 'UNSIGNED-PAYLOAD',
            'Content-Length': str(len(file.content)),
        }

        auth_data = AuthorizationData(
            method='PUT', canonical_uri=canonical_uri, datatime=datetime_, headers=headers, storage_data=self.__data
        )

        headers |= {'Authorization': _Authorization(auth_data).get_key()}

        try:
            await self.__request('PUT', f'https://{self.__data.host}{canonical_uri}', headers, file.content)
        except RequestError as error:
            raise UploadError(canonical_uri, error.response) from error

    async def __remove(self, path: Iterable[str]) -> None:
        datetime_ = datetime.now(UTC)
        canonical_uri = f'/{self.__data.bucket_name}'

        data = f'<Delete>{"".join(f"<Object><Key>{e}</Key></Object>" for e in path)}</Delete>'.encode()

        headers = {
            'Content-MD5': b64encode(md5(data).digest()).decode('ascii'),
            'X-Amz-Date': datetime_.strftime('%Y%m%dT%H%M%SZ'),
            'X-Amz-Content-SHA256': sha256(data).hexdigest(),
        }

        auth_data = AuthorizationData(
            method='POST',
            canonical_uri=canonical_uri,
            datatime=datetime_,
            headers=headers,
            params={'delete': ''},
            storage_data=self.__data
        )

        headers |= {'Authorization': _Authorization(auth_data).get_key()}

        try:
            await self.__request('POST', f'https://{self.__data.host}{canonical_uri}?delete', headers, data)
        except RequestError as error:
            raise DeleteError(path, error.response) from error

    async def __get_files(self, path: str) -> list[str]:
        datetime_ = datetime.now(UTC)
        canonical_uri = f'/{self.__data.bucket_name}'

        prefix = quote(path, '')

        headers = {
            'X-Amz-Date': datetime_.strftime('%Y%m%dT%H%M%SZ'),
            'X-Amz-Content-SHA256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        }

        auth_data = AuthorizationData(
            method='GET',
            canonical_uri=canonical_uri,
            datatime=datetime_,
            headers=headers,
            params={'prefix': prefix, 'encoding-type': 'url'},
            storage_data=self.__data
        )

        headers |= {'Authorization': _Authorization(auth_data).get_key()}

        try:
            response = await self.__request(
                'GET', f'https://{self.__data.host}{canonical_uri}?prefix={prefix}&encoding-type=url', headers
            )
        except RequestError as error:
            raise GetFilesError(path, error.response) from error

        xml = ElementTree.XML(response.content.decode().replace(' xmlns="http://s3.amazonaws.com/doc/2006-03-01/"', '', 1))
        return [unquote(element.text) for element in xml.findall('Contents/Key')]

    async def upload(self, path: str, files: list[File] | File) -> None:
        if not path or path.startswith('/') or path.endswith('/'):
            raise WrongPathError(path)

        if not isinstance(files, list):
            files = [files]

        for file in files:
            if len(file.content) == 0:
                raise EmptyFileError(file)

            await self.__upload_file(path, file)

    async def remove(self, *path: str) -> None:
        paths = []

        for element in path:
            if not element or element.startswith('/'):
                raise WrongPathError(element)

            if element.endswith('/'):
                paths += await self.__get_files(element)
                continue

            paths.append(element)

        await self.__remove(paths)

    async def get_files(self, path: str) -> list[str]:
        if not path.endswith('/') or path.startswith('/'):
            raise WrongPathError(path)

        return await self.__get_files(path)

    async def disconnect(self) -> None:
        await self.__session.close()
