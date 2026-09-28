from datetime import date
from typing import Optional  # noqa: UP035 - SQLAlchemy resolves these forward refs by name

from sqlmodel import Field, Relationship, SQLModel


class TaskModel(SQLModel, table=True):  # type: ignore
    task_id: int | None = Field(default=None, primary_key=True, index=True)
    competition_id: int = Field(nullable=False, foreign_key="competitionmodel.competition_id")
    task_url: str = Field(nullable=False)
    task_name: str = Field(nullable=False)
    task_status: str = Field(nullable=False)
    task_order: int = Field(nullable=False)
    # The flight this task was set in. Nullable because WatchMeFly does not
    # always publish the Flights & Tasks view, and because competitions loaded
    # before this was scraped have no flight stored.
    flight_number: int | None = Field(default=None, index=True)
    flight_date: date | None = Field(default=None)
    flight_period: str | None = Field(default=None)

    competition: Optional["CompetitionModel"] = Relationship(back_populates="tasks")  # type: ignore # noqa
    task_results: list["TaskResultModel"] = Relationship(back_populates="task_results")  # type: ignore # noqa
