from parser.competitor import get_competitor_data
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from actions.competition import the_competition
from actions.utils import try_endpoint
from database import get_db
from models.competitor import CompetitorModel

router = APIRouter()


@router.get(
    "/get_competitors_in_competition",
    summary="Add a new list of competitors taking part in a competition",
)
@try_endpoint
async def get_competitors(
    competition_id: int, session: Session = Depends(get_db)
) -> List[CompetitorModel]:
    competition_to_parse = await the_competition(
        competition_id=competition_id, session=session
    )
    return get_competitor_data(competition_to_parse)
