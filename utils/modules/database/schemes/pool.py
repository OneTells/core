from pydantic import BaseModel


class DatabaseData(BaseModel):
    user: str
    password: str
    host: str
    name: str
    port: int

    @property
    def dsn(self) -> str:
        return f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'
