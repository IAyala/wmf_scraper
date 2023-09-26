from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TaskResultModel(SQLModel, table=True):  # type: ignore
    task_id: Optional[int] = Field(primary_key=True, foreign_key="taskmodel.task_id")
    competitor_id: Optional[int] = Field(
        primary_key=True, foreign_key="competitormodel.competitor_id"
    )
    tr_result: str = Field(nullable=False)
    tr_gross_score: int = Field(nullable=False)
    tr_task_penalty: int = Field(nullable=False)
    tr_competition_penalty: int = Field(nullable=False)
    tr_net_score: int = Field(nullable=False)
    tr_notes: str = Field()

    task_results: Optional["TaskModel"] = Relationship(back_populates="task_results")  # type: ignore # noqa
