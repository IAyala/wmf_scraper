from sqlmodel import SQLModel


class LoadCompetitionRequest(SQLModel):
    competition_id: int
