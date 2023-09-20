from typing import Dict

from fastapi import APIRouter

from actions.utils import try_endpoint
from common.environment import get_version

router = APIRouter()


@router.get("", summary="Returns the version of the code")
@try_endpoint
async def wmf_scraper_version() -> Dict[str, str]:
    return {"code_version": get_version()}
