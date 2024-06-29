import hashlib
from functools import wraps
from typing import Callable, Awaitable

from fastapi import BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.utils import is_body_allowed_for_status_code

from utils.modules.fastapi_cache.methods.auxiliary import edit_function_signature, run_function, set_value_in_storage
from utils.modules.fastapi_cache.methods.coder import Coder
from utils.modules.fastapi_cache.methods.key_builder import KeyBuilder
from utils.modules.fastapi_cache.methods.setting import Settings
from utils.modules.fastapi_cache.objects import logger


def cache[** P, R: Response](expire: int = None, coder: type[Coder] = None, key_builder: type[KeyBuilder] = None):
    def wrapper(func: Callable[P, Awaitable[R] | R]) -> Callable[P, Awaitable[R]]:
        (
            (request_name, is_add_request),
            (response_name, is_add_response),
            (background_tasks_name, is_add_background_tasks)
        ) = edit_function_signature(func)

        @wraps(func)
        async def inner(**kwargs: P.kwargs) -> R | None:
            clear_kwargs = kwargs.copy()

            if is_add_request:
                kwargs.pop(request_name)

            if is_add_response:
                kwargs.pop(response_name)

            if is_add_background_tasks:
                kwargs.pop(background_tasks_name)

            request: Request = clear_kwargs.pop(request_name)

            if request.method != "GET":
                return await run_function(func, kwargs)

            if request.headers.get("Cache-Control") in ("no-store", "no-cache"):
                return await run_function(func, kwargs)

            background_tasks: BackgroundTasks = clear_kwargs.pop(background_tasks_name)

            key = (key_builder or Settings.key_builder).build(func, kwargs=clear_kwargs)

            try:
                data_from_storage = await Settings.storage.get(key)
            except Exception as error:
                logger.warning(f'Не удалось взять данные из хранилища: {error}')
                data_from_storage = None

            if data_from_storage is not None:
                ttl, value_from_storage = data_from_storage

                old_etag = request.headers.get("if-none-match", None)
                new_etag = f"W/{hashlib.sha256(value_from_storage).hexdigest()}"

                if old_etag == new_etag:
                    response: Response = clear_kwargs.pop(response_name)
                    response.headers["Cache-Control"] = f"max-age={ttl}"
                    response.status_code = 304
                    return

                try:
                    result = (coder or Settings.coder).decode(value_from_storage)
                except Exception as error:
                    logger.warning(f'Не удалось сериализовать данные: {error}')
                    result = await run_function(func, kwargs)

                response = result if isinstance(result, Response) else clear_kwargs.pop(response_name)
                response.headers["Cache-Control"] = f"max-age={ttl}"
                response.headers["ETag"] = new_etag

                return result

            result = await run_function(func, kwargs)

            if isinstance(result, Response) and not is_body_allowed_for_status_code(result.status_code):
                result.body = b""

            try:
                result_decoded = (coder or Settings.coder).encode(result)
            except Exception as error:
                logger.warning(f'Не удалось сериализовать данные: {error}')
                return result

            background_tasks.add_task(set_value_in_storage, key, result_decoded, expire)

            result.headers["Cache-Control"] = f"max-age={expire}"
            result.headers["ETag"] = f"W/{hashlib.sha256(result_decoded).hexdigest()}"

            return result

        return inner

    return wrapper
