from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitorModel(SQLModel, table=True):  # type: ignore
    competitor_id: Optional[int] = Field(
        default=None, primary_key=True, index=True, nullable=False
    )
    name: str = Field(primary_key=True, nullable=False)
    country: str = Field(primary_key=True, nullable=False)
    banner_number: int = Field(nullable=False)
    competition_id: Optional[int] = Field(
        default=None, nullable=False, foreign_key="competitionmodel.competition_id"
    )
