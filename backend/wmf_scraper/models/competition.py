from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, SQLModel


class CompetitionPurgeResponse(SQLModel):
    competition_id_purged: int
    number_tasks_removed: int
    number_task_results_removed: int

    def __str__(self) -> str:
        message: str = f"Competition {self.competition_id_purged} has been purged. "
        message += f"{self.number_task_results_removed} tasks removed "
        message += f"and {self.number_task_results_removed} task results removed"
        return message


class CompetitionRequest(SQLModel):  # type: ignore
    competition_url: str = Field(unique=True)
    competition_description: str = Field(unique=True)


class CompetitionModel(CompetitionRequest, table=True):  # type: ignore
    competition_id: int | None = Field(default=None, primary_key=True, index=True)
    competition_load_time: datetime | None = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))

    tasks: list["TaskModel"] = Relationship(back_populates="competition")  # type: ignore # noqa
