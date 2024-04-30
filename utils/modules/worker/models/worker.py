from datetime import datetime

from sqlalchemy import Text
from sqlalchemy import text, Boolean, false
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column as column, Mapped

from utils.modules.database.objects.database import Base


class Worker(Base):
    __tablename__ = 'workers'

    name: Mapped[str] = column(Text, unique=True, primary_key=True)
    is_trigger_on: Mapped[bool] = column(Boolean, nullable=False, server_default=false())

    created_at: Mapped[datetime] = column(TIMESTAMP, nullable=False, server_default=text("now()"))
