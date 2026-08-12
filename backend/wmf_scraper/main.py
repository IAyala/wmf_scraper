import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from wmf_scraper.database import create_db_if_not_exists
from wmf_scraper.routers import (
    auth,
    competition,
    competitor,
    load,
    query,
    task,
    task_result,
    version,
)
from wmf_scraper.security import require_user
from wmf_scraper.settings import (
    get_credentials,
    get_session_secret,
    get_static_dir,
    get_version,
    is_development_mode,
)

load_dotenv()

API_PREFIX = "/api"

API_DESCRIPTION = """
REST API to retrieve and analyse balloon competition results from WatchMeFly.

## Authentication

Every endpoint below `/api` except `/api/version` and `/api/auth/*` requires
authentication, in one of two ways:

* **Session cookie** — `POST /api/auth/login` with `{"username", "password"}`.
  This is what the web UI uses.
* **API key** — send `Authorization: Bearer <API_KEY>`. Intended for scripts;
  it is granted the `superadmin` role.

Endpoints that modify data additionally require the `superadmin` role.
"""


def _check_production_configuration() -> None:
    """Refuse to start in production without the secrets we depend on."""
    if is_development_mode():
        logger.info("🔓 Development mode: relaxed configuration checks.")
        return

    problems = []
    if not get_session_secret():
        problems.append("SESSION_SECRET is not set, sessions cannot be signed")
    if not get_credentials():
        problems.append(
            "no login credentials configured; set ADMIN_USERNAME/ADMIN_PASSWORD "
            "and/or SUPERADMIN_USERNAME/SUPERADMIN_PASSWORD"
        )
    if problems:
        for problem in problems:
            logger.error(f"❌ {problem}")
        sys.exit(1)
    logger.info("✅ Authentication is configured.")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    _check_production_configuration()
    create_db_if_not_exists()
    yield


app = FastAPI(
    title="WMF Scraper",
    description=API_DESCRIPTION,
    version=get_version(),
    lifespan=lifespan,
    docs_url=f"{API_PREFIX}/docs",
    openapi_url=f"{API_PREFIX}/openapi.json",
    redoc_url=None,
)

# Public: the Fly health check hits /api/version, and login obviously cannot
# require a session.
app.include_router(version.router, prefix=f"{API_PREFIX}/version", tags=["Version"])
app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Auth"])

# Everything else needs a session (or an API key). The endpoints that modify
# data additionally depend on require_superadmin, declared in their router.
protected = [Depends(require_user)]
app.include_router(load.router, prefix=f"{API_PREFIX}/load", tags=["Load"], dependencies=protected)
app.include_router(query.router, prefix=f"{API_PREFIX}/query", tags=["Query"], dependencies=protected)
app.include_router(competition.router, prefix=f"{API_PREFIX}/competition", tags=["Competition"], dependencies=protected)
app.include_router(competitor.router, prefix=f"{API_PREFIX}/competitor", tags=["Competitor"], dependencies=protected)
app.include_router(task.router, prefix=f"{API_PREFIX}/task", tags=["Task"], dependencies=protected)
app.include_router(
    task_result.router, prefix=f"{API_PREFIX}/task_result", tags=["Task Results"], dependencies=protected
)

# Serve the built React app from the same origin, when it has been built into
# the image. Registered last so it never shadows an API route.
_static_dir = get_static_dir()

if _static_dir is not None:
    static_root = _static_dir.resolve()
    index_html = static_root / "index.html"
    logger.info(f"🖥️  Serving frontend from {static_root}")
    app.mount("/assets", StaticFiles(directory=static_root / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        """Return the requested static file, else index.html for client routing."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = (static_root / full_path).resolve()
        if full_path and candidate.is_relative_to(static_root) and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index_html)
