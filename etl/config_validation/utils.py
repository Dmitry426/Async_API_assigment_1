from datetime import datetime
from typing import Optional

from pydantic.main import BaseModel


class DatetimeSerialization(BaseModel):
    persons_updated_at: Optional[datetime] = None
    genres_updated_at: Optional[datetime] = None
    film_work_updated_at: Optional[datetime] = None
