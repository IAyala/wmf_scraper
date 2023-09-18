from typing import Optional

from sqlmodel import Field, SQLModel


class TaskResultModel(SQLModel, table=True):  # type: ignore
    result: str = Field(nullable=False)
    gross_score: int = Field(nullable=False)
    task_penalty: int = Field(nullable=False)
    competition_penalty: int = Field(nullable=False)
    net_score: int = Field(nullable=False)
    notes: str = Field()
    task_result_id: Optional[int] = Field(
        primary_key=True, nullable=False, foreign_key="taskmodel.task_id"
    )
    competitor_name: str = Field(
        primary_key=True, nullable=False, foreign_key="competitormodel.name"
    )
    competition_id: int = Field(
        primary_key=True, nullable=False, foreign_key="competitionmodel.competition_id"
    )
