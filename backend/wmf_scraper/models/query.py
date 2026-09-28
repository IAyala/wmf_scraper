from datetime import date

from sqlmodel import Field, SQLModel


class CompetitorResults(SQLModel):
    result: str = Field(nullable=False)
    gross_score: int = Field(nullable=False)
    task_penalty: int = Field(nullable=False)
    competition_penalty: int = Field(nullable=False)
    net_score: int = Field(nullable=False)
    notes: str = Field()
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)
    competition_name: str = Field(nullable=False)
    task_order: int = Field(nullable=False)
    task_name: str = Field(nullable=False)
    task_status: str = Field(nullable=False)
    flight_number: int | None = Field(default=None)
    flight_date: date | None = Field(default=None)
    flight_period: str | None = Field(default=None)


class CountryResults(SQLModel):
    competitor_country: str = Field(nullable=False)
    number_competitors: int = Field(nullable=False)
    average_score: float = Field(nullable=False)


class CountryResultsWithPosition(CountryResults):
    position: int = Field(nullable=False)


class CompetitionOverall(SQLModel):
    total_score: int = Field(nullable=False)
    average_score: float = Field(nullable=False)
    total_competition_penalty: int = Field(nullable=False)
    total_task_penalty: int = Field(nullable=False)
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)


class CompetitionOverallWithPosition(CompetitionOverall):
    position: int = Field(nullable=False)


class CompetitorOverallByTask(SQLModel):
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)
    # Parallel to competitor_positions: the real task numbers, which skip any
    # task that was cancelled and never published.
    task_orders: list[int] = Field(default=[])
    competitor_positions: list[int] = Field(default=[])


class TaskInCompetition(SQLModel):
    """A task as it is stored, for picking one to look at."""

    task_order: int = Field(nullable=False)
    task_name: str = Field(nullable=False)
    task_status: str = Field(nullable=False)
    flight_number: int | None = Field(default=None)
    flight_date: date | None = Field(default=None)
    flight_period: str | None = Field(default=None)


class TaskResult(SQLModel):
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)
    result: str = Field(nullable=False)
    gross_score: int = Field(nullable=False)
    task_penalty: int = Field(nullable=False)
    competition_penalty: int = Field(nullable=False)
    net_score: int = Field(nullable=False)
    notes: str = Field()


class TaskResultWithPosition(TaskResult):
    position: int = Field(nullable=False)


class FlightInCompetition(SQLModel):
    """One flight of a competition, with the tasks that were set in it."""

    flight_number: int = Field(nullable=False)
    flight_date: date | None = Field(default=None)
    flight_period: str | None = Field(default=None)
    task_orders: list[int] = Field(default=[])


class RFSPenaltiesByCompetition(SQLModel):
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)
    task_number: int = Field(nullable=False)
    task_description: str = Field(nullable=False)
    task_penalty: int = Field(nullable=False)
    competition_penalty: int = Field(nullable=False)
    notes: str = Field()
