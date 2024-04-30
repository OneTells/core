import os as _os
from sys import stderr as _stderr

from loguru import logger as _logger

from .modules import *
from .modules.logger.handlers.telegram import Telegram

__version__ = "1.0.6"


def add_logger_handlers(path: str, token: str, chat_id: int) -> None:
    _logger.add(
        _stderr, level="INFO",
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True
    )

    _logger.add(
        Telegram(token, chat_id), level='WARNING',
        filter=lambda x: 'unit' in x['extra']
    )

    _os.makedirs(path, exist_ok=True)

    _logger.add(
        f'{path}/info.log', level='INFO',
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )

    _logger.add(
        f'{path}/debug.log', level='DEBUG',
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )


_logger.disable('utils')

__all__ = (
    '__version__',
    "add_logger_handlers"
)
