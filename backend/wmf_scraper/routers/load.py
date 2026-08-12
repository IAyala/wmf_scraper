from fastapi import APIRouter, Depends
from sqlmodel import Session

from wmf_scraper.actions.load import load_competition_helper
from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.database import get_db
from wmf_scraper.models.load import LoadCompetitionRequest, LoadCompetitionResponse
from wmf_scraper.security import User, require_superadmin

router = APIRouter()


@router.post("/load_one_competition", summary="Load One Competition Results")
@try_endpoint
async def load_one_competition(
    competition_id: int,
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> LoadCompetitionResponse | None:
    return await load_competition_helper(competition_id=competition_id, session=session)


@router.post("/load_many_competitions", summary="Load Many Competition Results")
@try_endpoint
async def load_many_competitions(
    req: list[LoadCompetitionRequest],
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> list[LoadCompetitionResponse]:
    result: list[LoadCompetitionResponse] = []
    for elem in req:
        result.append(await load_competition_helper(competition_id=elem.competition_id, session=session))
    return result
