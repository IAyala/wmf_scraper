from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, column, func, select

from database import get_db
from models.competition import (
    CompetitionModel,
    CompetitionRequest,
    LoadCompetitionRequest,
)
from routers.task import load_tasks_for_competition
from routers.task_result import load_task_results

router = APIRouter()


async def how_many_competitions(session: Session) -> int:
    result = session.exec(select([func.count(CompetitionModel.competition_id)])).one()
    return result  # type: ignore


@router.post("/add", summary="Add a new competition to the scraper")
async def add_competition(
    req: CompetitionRequest, session: Session = Depends(get_db)
) -> CompetitionModel:
    num_prev_competitions = await how_many_competitions(session)
    try:
        to_add = CompetitionModel(**req.dict())
        to_add.competition_id = num_prev_competitions + 1
        session.add(to_add)
        session.commit()
        return CompetitionModel(**req.dict(), competition_id=num_prev_competitions + 1)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"{ex}") from ex


@router.get(
    "/get_by_description", summary="Gets the competition details by description"
)
async def get_by_description(
    description: str, session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    return session.exec(
        select(CompetitionModel).where(column("description").contains(description))
    ).all()


@router.get("/all", summary="Gets the competition details by description")
async def get_all_competitions(
    session: Session = Depends(get_db),
) -> List[CompetitionModel]:
    return session.exec(select(CompetitionModel)).all()


@router.post("/load_results", summary="Load Competition Results")
async def load_competition(
    req: LoadCompetitionRequest, session: Session = Depends(get_db)
) -> dict:
    the_competition = session.exec(
        select(CompetitionModel).where(
            CompetitionModel.competition_id == req.competition_id
        )
    ).all()
    if not the_competition:
        raise HTTPException(
            status_code=400, detail=f"Competition ID: {req.competition_id} not found"
        )
    competition_to_update = the_competition[0]
    competition_to_update.load_time = datetime.now()
    tasks_added = await load_tasks_for_competition(req.competition_id, session=session)
    task_results_added = []
    for task_to_add in tasks_added:
        task_results_added.append(
            await load_task_results(competition_to_update, task_to_add, session=session)
        )
    return {
        "updated_competition": competition_to_update,
        "tasks_added": len(tasks_added),
        "task_results_added": [len(x) for x in task_results_added],
    }
