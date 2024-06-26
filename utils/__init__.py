from loguru import logger as _logger

from .modules import *
from .modules.logger.handlers.telegram import Telegram

__version__ = "1.5.15"

_logger.disable('utils')

__all__ = (
    '__version__'
)
