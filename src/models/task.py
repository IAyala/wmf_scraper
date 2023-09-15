from sqlmodel import Field, SQLModel


class TaskModel(SQLModel, table=True):  # type: ignore
    url: str = Field(primary_key=True, nullable=False)
    name: str = Field(nullable=False)
    status: str = Field(nullable=False)
    task_id: int = Field(nullable=False)
    competition_id: int = Field(
        nullable=False, foreign_key="competitionmodel.competition_id"
    )
