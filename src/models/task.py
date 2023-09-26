from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TaskModel(SQLModel, table=True):  # type: ignore
    task_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    competition_id: int = Field(
        nullable=False, foreign_key="competitionmodel.competition_id"
    )
    task_url: str = Field(nullable=False)
    task_name: str = Field(nullable=False)
    task_status: str = Field(nullable=False)
    task_order: int = Field(nullable=False)

    competition: Optional["CompetitionModel"] = Relationship(back_populates="tasks")  # type: ignore # noqa
    task_results: List["TaskResultModel"] = Relationship(back_populates="task_results")  # type: ignore # noqa
