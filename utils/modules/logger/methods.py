import os
from sys import stderr

from loguru import logger

from .handlers.telegram import Telegram
from .objects import FORMAT, FILTER
from .schemes import TelegramData


def enable_logger() -> None:
    logger.enable('utils')
    logger.remove()


def add_logger_to_console() -> None:
    logger.add(
        stderr, level="INFO",
        format=FORMAT,
        filter=FILTER,
        backtrace=True, diagnose=True
    )


def add_logger_to_telegram(data: TelegramData) -> None:
    logger.add(
        Telegram(data), level='WARNING',
        filter=FILTER
    )


def add_logger_to_file(path: str) -> None:
    os.makedirs(path, exist_ok=True)

    logger.add(
        f'{path}/info.log', level='INFO',
        format=FORMAT,
        filter=FILTER,
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )

    logger.add(
        f'{path}/debug.log', level='DEBUG',
        format=FORMAT,
        filter=FILTER,
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )
