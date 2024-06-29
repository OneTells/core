from utils.modules.fastapi_cache.methods.coder import Coder, ResponseCoder
from utils.modules.fastapi_cache.methods.key_builder import KeyBuilder, DefaultKeyBuilder
from utils.modules.fastapi_cache.methods.storage import Storage, MemoryStorage


class Settings:
    coder: type[Coder]
    key_builder: type[KeyBuilder]
    storage: type[Storage]

    @classmethod
    def set(cls, *, coder: type[Coder] = None, key_builder: type[KeyBuilder] = None, storage: type[Storage] = None):
        cls.coder = coder or ResponseCoder
        cls.key_builder = key_builder or DefaultKeyBuilder
        cls.storage = storage or MemoryStorage
