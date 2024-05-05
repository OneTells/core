from loguru import logger as _logger

from .modules import *
from .modules.logger.handlers.telegram import Telegram

__version__ = "1.0.9"

_logger.disable('utils')

__all__ = (
    '__version__'
)
