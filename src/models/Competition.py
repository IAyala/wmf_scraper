from typing import Optional

from sqlmodel import Field, SQLModel


class Competition(SQLModel, table=True):  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)  # Autoincrement
    url: str
    description: str
