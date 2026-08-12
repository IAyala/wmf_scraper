from fastapi import APIRouter, Depends
from sqlmodel import Session

from wmf_scraper.actions.competition import the_competition
from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.database import get_db
from wmf_scraper.models.task import TaskModel
from wmf_scraper.parsers.task import get_tasks_data

router = APIRouter()


@router.get("/get_tasks_for_competition", summary="Add a new competition to the scraper")
@try_endpoint
async def get_tasks_for_competition(competition_id: int, session: Session = Depends(get_db)) -> list[TaskModel]:
    competition_to_update = await the_competition(competition_id=competition_id, session=session)
    return get_tasks_data(competition_to_update)
