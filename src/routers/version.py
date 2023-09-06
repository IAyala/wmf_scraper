from fastapi import APIRouter

from common.environment import get_version

router = APIRouter()


@router.get("/code", summary="Returns the version of the code")
async def wmf_scraper_version() -> str:
    the_version = get_version()
    return the_version if the_version else ""
