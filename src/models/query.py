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


class CompetitionOverall(SQLModel):
    total_score: int = Field(nullable=False)
    total_competition_penalty: int = Field(nullable=False)
    total_task_penalty: int = Field(nullable=False)
    competitor_name: str = Field(nullable=False)
    competitor_country: str = Field(nullable=False)
