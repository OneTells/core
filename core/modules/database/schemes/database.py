from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import Update as Update_, Select as Select_, Delete as Delete_
from sqlalchemy.dialects.postgresql import Insert as _Insert
from sqlalchemy.sql.dml import ReturningInsert

T = TypeVar('T', bound=BaseModel)
Result = TypeVar('Result')

Query = Select_ | Update_ | _Insert | Delete_ | ReturningInsert
