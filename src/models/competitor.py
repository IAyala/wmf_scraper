from typing import Optional

from sqlmodel import Field, SQLModel


class CompetitorSimpleModel(SQLModel):
    name: str = Field(unique=True, nullable=False)
    country: str = Field(nullable=False)


class CompetitorModel(CompetitorSimpleModel, table=True):  # type: ignore
    competitor_id: Optional[int] = Field(
        default=None, primary_key=True, index=True, nullable=False
    )
