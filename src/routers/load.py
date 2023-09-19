from datetime import datetime
from parser.task import get_tasks_data
from parser.task_results import get_task_results
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from actions.utils import try_endpoint
from database import get_db
from models.competition import CompetitionModel
from models.load import LoadCompetitionRequest
from models.task import TaskModel
from models.task_result import TaskResultModel

router = APIRouter()


async def the_competition(competition_id: int, session: Session) -> CompetitionModel:
    the_competition = session.exec(
        select(CompetitionModel).where(
            CompetitionModel.competition_id == competition_id
        )
    )
    if not the_competition.one_or_none():
        raise ValueError(f"Competition ID: {competition_id} not found")
    return the_competition.one()


async def load_tasks_for_competition(
    competition: CompetitionModel, session: Session
) -> List[TaskModel]:
    async def remove_previous_tasks():
        prev_tasks = session.exec(
            select(TaskModel).where(
                TaskModel.competition_id == competition.competition_id
            )
        )
        for task in prev_tasks:
            session.delete(task)
        session.commit()

    async def add_new_tasks(tasks_to_add: List[TaskModel]) -> List[TaskModel]:
        for updated_task in tasks_to_add:
            session.add(updated_task)
        session.commit()
        return session.exec(
            select(TaskModel).where(
                TaskModel.competition_id == competition.competition_id
            )
        ).all()

    await remove_previous_tasks()
    return await add_new_tasks(get_tasks_data(competition))


async def load_task_results_for_competition(
    competition: CompetitionModel, task: TaskModel, session: Session
) -> List[TaskResultModel]:
    async def remove_previous_task_results():
        prev_task_results = session.exec(
            select(TaskResultModel).where(
                TaskResultModel.task_result_id == task.task_id
            )
        )
        for prev_task_result in prev_task_results:
            session.delete(prev_task_result)
        session.commit()

    async def add_new_task_results(
        task_results_to_add: List[TaskResultModel],
    ) -> List[TaskResultModel]:
        for updated_task_result in task_results_to_add:
            session.add(updated_task_result)
        session.commit()
        return session.exec(
            select(TaskResultModel)
            .where(TaskResultModel.competition_id == competition.competition_id)
            .where(TaskResultModel.task_result_id == task.task_id)
        ).all()

    await remove_previous_task_results()
    return await add_new_task_results(
        get_task_results(competition.competition_id, task)
    )


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
