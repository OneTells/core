import os
from sys import stderr

from loguru import logger

from .handlers.telegram import Telegram
from .schemes import TelegramData


def enable_logger(path: str = None, telegram_data: TelegramData = None) -> None:
    logger.enable('utils')

    logger.remove()
    logger.add(
        stderr, level="INFO",
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True
    )

    if telegram_data is not None:
        logger.add(
            Telegram(telegram_data.token, telegram_data.chat_id), level='WARNING',
            filter=lambda x: 'context' in x['extra']
        )

    if path is not None:
        os.makedirs(path, exist_ok=True)

        logger.add(
            f'{path}/info.log', level='INFO',
            format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
            filter=lambda x: 'context' in x['extra'],
            backtrace=True, diagnose=True, enqueue=True,
            compression='tar.xz', retention='10 days', rotation='100 MB'
        )

        logger.add(
            f'{path}/debug.log', level='DEBUG',
            format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
            filter=lambda x: 'context' in x['extra'],
            backtrace=True, diagnose=True, enqueue=True,
            compression='tar.xz', retention='10 days', rotation='100 MB'
        )
