from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from actions.load import load_competition_helper
from actions.utilities import try_endpoint
from database import get_db
from models.load import LoadCompetitionRequest, LoadCompetitionResponse

router = APIRouter()


@router.post("/load_one_competition", summary="Load One Competition Results")
@try_endpoint
async def load_one_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> Optional[LoadCompetitionResponse]:
    return await load_competition_helper(competition_id=competition_id, session=session)


@router.post("/load_many_competitions", summary="Load Many Competition Results")
@try_endpoint
async def load_many_competitions(
    req: List[LoadCompetitionRequest], session: Session = Depends(get_db)
) -> List[LoadCompetitionResponse]:
    result: List[LoadCompetitionResponse] = []
    for elem in req:
        result.append(
            await load_competition_helper(
                competition_id=elem.competition_id, session=session
            )
        )
    return result
