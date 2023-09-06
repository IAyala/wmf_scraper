import uvicorn
from fastapi import FastAPI

from common.environment import get_version
from routers import version

app = FastAPI(
    title="WMF_Scraper",
    description="This is a REST API to retrieve competition results from WatchMeFly website",
    version=get_version(),
)


app.include_router(version.router, prefix="/version")


if __name__ == "__main__":
    uvicorn.run(  # pragma: no cover
        "main:app",
        host="0.0.0.0",
        headers=[("server", "template")],
        reload=True,
        port=8000,
    )
