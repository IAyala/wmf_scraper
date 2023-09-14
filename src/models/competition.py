from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitionRequest(SQLModel):
    url: str
    description: str


class CompetitionModel(CompetitionRequest, table=True):  # type: ignore
    competition_id: int = Field(primary_key=True, index=True, nullable=False)
    url: str = Field(primary_key=True, unique=True)
    load_time: Optional[datetime] = Field(default=None)
