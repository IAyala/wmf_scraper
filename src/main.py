import uvicorn
from fastapi import FastAPI
from fastapi_utils.timing import add_timing_middleware
from loguru import logger

from common.environment import get_version
from database import create_db_if_not_exists
from routers import competition, competitor, load, query, task, task_result, version

app = FastAPI(
    title="WMF_Scraper",
    description="This is a REST API to retrieve competition results from WatchMeFly website",
    version=get_version(),
)

add_timing_middleware(app, record=logger.debug, prefix="app", exclude="untimed")

app.include_router(version.router, prefix="/version", tags=["Version"])
app.include_router(load.router, prefix="/load", tags=["Load"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(competition.router, prefix="/competition", tags=["Competition"])
app.include_router(competitor.router, prefix="/competitor", tags=["Competitor"])
app.include_router(task.router, prefix="/task", tags=["Task"])
app.include_router(task_result.router, prefix="/task_result", tags=["Task Results"])

create_db_if_not_exists()

if __name__ == "__main__":
    uvicorn.run(  # pragma: no cover
        "main:app",
        host="0.0.0.0",
        headers=[("server", "template")],
        reload=True,
        port=8000,
    )
