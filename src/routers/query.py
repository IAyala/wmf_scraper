from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from actions.query import (
    query_overall_results_for_competition,
    query_positions_by_competitor_in_competition,
    query_result_for_competitor_in_competition,
)
from actions.utilities import try_endpoint
from database import get_db
from models.query import (
    CompetitionOverallWithPosition,
    CompetitorOverallByTask,
    CompetitorResults,
)

router = APIRouter()


@router.get(
    "/results_competitor_in_competition",
    summary="Load Results for a Competitor in a Competition",
)
@try_endpoint
async def results_competitor_in_competition(
    competition_id: int, competitor_name: str, session: Session = Depends(get_db)
) -> List[CompetitorResults]:
    return await query_result_for_competitor_in_competition(
        competition_id=competition_id, competitor_name=competitor_name, session=session
    )


@router.get(
    "/overall_results_competition",
    summary="Overall Results for a Competition",
)
@try_endpoint
async def overall_results_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[CompetitionOverallWithPosition]:
    return await query_overall_results_for_competition(
        competition_id=competition_id, session=session
    )


@router.get(
    "/position_path_in_competition",
    summary="Positions held in total results by task for a competitor",
)
@try_endpoint
async def position_path_in_competition(
    competition_id: int, competitor_name: str, session: Session = Depends(get_db)
) -> CompetitorOverallByTask:
    return await query_positions_by_competitor_in_competition(
        competition_id=competition_id, competitor_name=competitor_name, session=session
    )
