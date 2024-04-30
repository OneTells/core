import loguru
import requests
from requests import RequestException

from utils.general.utils.counter import FloodControl
from utils.modules.database.objects.logger import logger


class Telegram:
    __flood_control = FloodControl(15, minutes=1)

    def __init__(self, token: str, chat_id: int) -> None:
        self.__token = token
        self.__chat_id = chat_id

    def __call__(self, message: "loguru.Message") -> None:
        if not self.__flood_control.add():
            return

        text = (
            f'{message.record['level'].name.upper()} | '
            f'<{', '.join(f'{e=}' for e in message.record['extra'].values())}> | '
            f'{message.record['message'] or "..."}'
        )

        try:
            requests.get(
                f'https://api.telegram.org/bot{self.__token}/sendMessage',
                json={'chat_id': self.__chat_id, 'text': text[:4095]}
            )
        except RequestException:
            logger.exception(f'Ошибка при отправки логов: {message}')
