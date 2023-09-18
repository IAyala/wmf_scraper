from parser.task import get_tasks_data
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_db
from models.competition import CompetitionModel
from models.task import TaskModel

router = APIRouter()


@router.get(
    "/get_tasks_for_competition", summary="Add a new competition to the scraper"
)
async def get_tasks_for_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[TaskModel]:
    try:
        result = session.exec(
            select(CompetitionModel).where(
                CompetitionModel.competition_id == competition_id
            )
        ).all()
        if result:
            return get_tasks_data(result[0])
        return []
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"{ex}") from ex


@router.post(
    "/load_tasks_for_competition", summary="Load tasks into db for a given competition"
)
async def load_tasks_for_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[TaskModel]:
    try:
        result = session.exec(
            select(CompetitionModel).where(
                CompetitionModel.competition_id == competition_id
            )
        ).all()
        if result:
            prev_tasks = session.exec(
                select(TaskModel).where(TaskModel.competition_id == competition_id)
            )
            for task in prev_tasks:
                session.delete(task)
            session.commit()
            tasks_to_add = get_tasks_data(result[0])
            for updated_task in tasks_to_add:
                session.add(updated_task)
            session.commit()
            return session.exec(
                select(TaskModel).where(TaskModel.competition_id == competition_id)
            ).all()
        return []
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"{ex}") from ex
