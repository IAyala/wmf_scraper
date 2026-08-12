from sqlmodel import Field, SQLModel


class CompetitorModel(SQLModel, table=True):  # type: ignore
    competitor_id: int | None = Field(default=None, primary_key=True, index=True)
    competitor_name: str = Field(unique=True, nullable=False)
    competitor_country: str = Field(nullable=False)


class CountryModel(SQLModel):  # type: ignore
    competitor_country: str = Field(nullable=False)
