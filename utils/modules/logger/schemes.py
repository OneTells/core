from pydantic import BaseModel


class TelegramData(BaseModel):
    token: str
    chat_id: int
