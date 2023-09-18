from parser.task_results import get_task_results, get_tasks_results_data
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_db
from models.competition import CompetitionModel
from models.task import TaskModel
from models.task_result import TaskResultModel

router = APIRouter()


@router.get(
    "/get_task_results_for_competition", summary="Add a new competition to the scraper"
)
async def get_task_results_for_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[TaskResultModel]:
    try:
        result = session.exec(
            select(CompetitionModel).where(
                CompetitionModel.competition_id == competition_id
            )
        ).all()
        if result:
            return get_tasks_results_data(result[0])
        return []
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"{ex}") from ex


@router.post(
    "/load_task_results", summary="Load tasks results into db for a given task"
)
async def load_task_results(
    competition_info: CompetitionModel,
    task_info: TaskModel,
    session: Session = Depends(get_db),
) -> List[TaskResultModel]:
    try:
        prev_tasks = session.exec(
            select(TaskResultModel).where(
                TaskResultModel.task_result_id == task_info.task_id
            )
        )
        for task in prev_tasks:
            session.delete(task)
        session.commit()
        task_results_to_add = get_task_results(
            competition_info.competition_id, task_info
        )
        for updated_task_result in task_results_to_add:
            session.add(updated_task_result)
        session.commit()
        return session.exec(
            select(TaskResultModel)
            .where(TaskResultModel.competition_id == competition_info.competition_id)
            .where(TaskResultModel.task_result_id == task_info.task_id)
        ).all()
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"{ex}") from ex
