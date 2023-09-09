import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel

from common.environment import get_version
from database import db_engine
from routers import competition, version

app = FastAPI(
    title="WMF_Scraper",
    description="This is a REST API to retrieve competition results from WatchMeFly website",
    version=get_version(),
)

app.include_router(version.router, prefix="/version", tags=["Version"])
app.include_router(competition.router, prefix="/competition", tags=["Competition"])

SQLModel.metadata.create_all(db_engine.engine)


if __name__ == "__main__":
    uvicorn.run(  # pragma: no cover
        "main:app",
        host="0.0.0.0",
        headers=[("server", "template")],
        reload=True,
        port=8000,
    )
