import asyncio
import inspect
from inspect import Parameter
from typing import Awaitable, Callable

from fastapi import BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi.requests import Request
from fastapi.responses import Response

from utils.modules.fastapi_cache.methods.setting import Settings
from utils.modules.fastapi_cache.objects import logger


async def run_function[** P, R](func: Callable[P, Awaitable[R] | R], kwargs: P) -> R:
    if asyncio.iscoroutinefunction(func):
        return await func(**kwargs)

    return await run_in_threadpool(func, **kwargs)


def edit_function_signature(func: Callable) -> tuple[tuple[str, bool], tuple[str, bool], tuple[str, bool]]:
    request_parameter: Parameter | None = None
    is_add_request = False

    response_parameter: Parameter | None = None
    is_add_response = False

    background_tasks_parameter: Parameter | None = None
    is_add_background_tasks = False

    signature = inspect.signature(func)

    parameters: list[Parameter] = []

    for parameter in signature.parameters.values():
        if parameter.annotation is Request:
            request_parameter = parameter
        elif parameter.annotation is Response:
            response_parameter = parameter
        elif parameter.annotation is BackgroundTasks:
            background_tasks_parameter = parameter

        parameters.append(parameter)

    if request_parameter is None:
        parameters.append(
            request_parameter := Parameter(
                name="request",
                annotation=Request,
                kind=Parameter.KEYWORD_ONLY
            )
        )

        is_add_request = True

    if response_parameter is None:
        parameters.append(
            response_parameter := Parameter(
                name="response",
                annotation=Response,
                kind=Parameter.KEYWORD_ONLY
            )
        )

        is_add_response = True

    if background_tasks_parameter is None:
        parameters.append(
            background_tasks_parameter := Parameter(
                name="background_tasks",
                annotation=BackgroundTasks,
                kind=Parameter.KEYWORD_ONLY
            )
        )

        is_add_background_tasks = True

    func.__signature__ = signature.replace(parameters=parameters)

    return (
        (request_parameter.name, is_add_request),
        (response_parameter.name, is_add_response),
        (background_tasks_parameter.name, is_add_background_tasks)
    )


async def set_value_in_storage(key: str, value: bytes, expire: int | None):
    try:
        await Settings.storage.set(key, value, expire)
    except Exception as error:
        logger.warning(f"Не удалось записать данные в хранилище: {error}")
