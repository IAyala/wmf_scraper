from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class CompetitionPurgeResponse(SQLModel):
    competition_id_purged: int
    number_tasks_removed: int
    number_task_results_removed: int


class CompetitionRequest(SQLModel):  # type: ignore
    competition_url: str = Field(unique=True)
    competition_description: str = Field(unique=True)


class CompetitionModel(CompetitionRequest, table=True):  # type: ignore
    competition_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    competition_load_time: Optional[datetime] = Field(default=None)

    tasks: List["TaskModel"] = Relationship(back_populates="competition")  # type: ignore # noqa
