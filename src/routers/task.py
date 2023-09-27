from parser.task import get_tasks_data
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from actions.competition import the_competition
from actions.utilities import try_endpoint
from database import get_db
from models.task import TaskModel

router = APIRouter()


@router.get(
    "/get_tasks_for_competition", summary="Add a new competition to the scraper"
)
@try_endpoint
async def get_tasks_for_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[TaskModel]:
    competition_to_update = await the_competition(
        competition_id=competition_id, session=session
    )
    return get_tasks_data(competition_to_update)
