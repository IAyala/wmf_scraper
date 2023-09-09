from sqlmodel import Field, SQLModel


class CompetitionRequest(SQLModel):
    url: str
    description: str
    # load_time: datetime


class CompetitionModel(CompetitionRequest, table=True):  # type: ignore
    # competition_id: Optional[int] = Field(default=None, primary_key=True)  # Autoincrement
    url: str = Field(primary_key=True)
