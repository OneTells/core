from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from utils.modules.requests.schemes.sessions import Methods


class ContentType(str, Enum):
    JPEG = 'image/jpeg'
    PNG = 'image/png'


class File(BaseModel):
    name: str
    content: bytes
    type: ContentType


class StorageData(BaseModel):
    bucket_name: str
    secret_key: str
    access_key: str
    service: str = 's3'
    host: str
    region: str


class AuthorizationData(BaseModel):
    method: Methods
    canonical_uri: str
    datatime: datetime
    headers: dict[str, str]
    params: dict[str, str] = Field(default_factory=dict)

    storage_data: StorageData
