from typing import Optional

from sqlmodel import Field, SQLModel


class TaskModel(SQLModel, table=True):  # type: ignore
    task_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: str = Field(nullable=False)
    name: str = Field(nullable=False)
    status: str = Field(nullable=False)
    task_order: int = Field(nullable=False)
    competition_id: int = Field(
        nullable=False, foreign_key="competitionmodel.competition_id"
    )
