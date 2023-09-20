from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitionRequest(SQLModel):
    url: str
    description: str


class LoadCompetitionRequest(SQLModel):
    competition_id: int


class CompetitionModel(CompetitionRequest, table=True):  # type: ignore
    competition_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: str = Field(unique=True)
    description: str = Field(unique=True)
    load_time: Optional[datetime] = Field(default=None)
