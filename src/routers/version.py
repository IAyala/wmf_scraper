from typing import Dict

from fastapi import APIRouter

from common.environment import get_version

router = APIRouter()


@router.get("", summary="Returns the version of the code")
async def wmf_scraper_version() -> Dict[str, str]:
    return {"code_version": get_version()}
