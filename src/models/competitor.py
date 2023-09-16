from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitorSimpleModel(SQLModel):
    name: str = Field(primary_key=True, nullable=False)
    country: str = Field(primary_key=True, nullable=False)
    banner: str = Field(nullable=False)
    competition_id: Optional[int] = Field(
        default=None, nullable=False, foreign_key="competitionmodel.competition_id"
    )


class CompetitorModel(CompetitorSimpleModel, table=True):  # type: ignore
    competitor_id: Optional[int] = Field(
        default=None, primary_key=True, index=True, nullable=False
    )
