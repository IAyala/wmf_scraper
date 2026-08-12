from fastapi import APIRouter

from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.settings import get_version

router = APIRouter()


@router.get("", summary="Returns the version of the code")
@try_endpoint
async def wmf_scraper_version() -> dict[str, str]:
    return {"code_version": get_version()}
