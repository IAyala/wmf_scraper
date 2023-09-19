from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from actions.competition import the_competition
from actions.load import load_task_results_for_competition, load_tasks_for_competition
from actions.utils import try_endpoint
from database import get_db
from models.load import LoadCompetitionRequest

router = APIRouter()


@router.post("/load_competition", summary="Load Competition Results")
@try_endpoint
async def load_competition(
    req: LoadCompetitionRequest, session: Session = Depends(get_db)
) -> dict:
    competition_to_update = await the_competition(req.competition_id, session=session)
    competition_to_update.load_time = datetime.now()
    tasks_added = await load_tasks_for_competition(
        competition_to_update, session=session
    )
    results_added = {}
    for task_to_add in tasks_added:
        results_added[task_to_add] = await load_task_results_for_competition(
            competition_to_update, task_to_add, session=session
        )
    return results_added


@router.post("/load_many_competitions", summary="Load Competition Results")
@try_endpoint
async def load_many_competitions(
    req: List[LoadCompetitionRequest], session: Session = Depends(get_db)
) -> List[dict]:
    result = []
    for elem in req:
        result.append(await load_competition(elem, session=session))
    return result
