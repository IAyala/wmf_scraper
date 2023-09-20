from datetime import datetime
from parser.task import get_tasks_data
from parser.task_results import get_task_results
from typing import List

from sqlmodel import Session, select

from actions.competition import the_competition
from models.competition import CompetitionModel
from models.load import (
    LoadCompetitionRequest,
    LoadCompetitionResponse,
    LoadCompetitionTaskResultsResponse,
)
from models.task import TaskModel
from models.task_result import TaskResultModel


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

    async def add_new_tasks(tasks_to_add: List[TaskModel]) -> List[TaskModel]:
        for updated_task in tasks_to_add:
            session.add(updated_task)
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

    async def add_new_task_results(
        task_results_to_add: List[TaskResultModel],
    ) -> List[TaskResultModel]:
        for updated_task_result in task_results_to_add:
            session.add(updated_task_result)
        return session.exec(
            select(TaskResultModel)
            .where(TaskResultModel.competition_id == competition.competition_id)
            .where(TaskResultModel.task_result_id == task.task_id)
        ).all()

    await remove_previous_task_results()
    return await add_new_task_results(
        get_task_results(competition.competition_id, task)
    )


async def load_competition_helper(
    req: LoadCompetitionRequest, session: Session
) -> LoadCompetitionResponse:
    with session.begin():
        competition_to_update = await the_competition(
            req.competition_id, session=session
        )
        competition_to_update.load_time = datetime.now()
        response_dict = {
            "competition_loaded": competition_to_update.dict(),
            "tasks_loaded": [],
        }
        tasks_added = await load_tasks_for_competition(
            competition_to_update, session=session
        )
        for task_to_add in tasks_added:
            response_dict["tasks_loaded"].append(  # type:ignore
                LoadCompetitionTaskResultsResponse(
                    **{
                        "task_loaded": TaskModel(**task_to_add.dict()),
                        "task_results_loaded": [
                            TaskResultModel(**x.dict())
                            for x in await load_task_results_for_competition(
                                competition_to_update, task_to_add, session=session
                            )
                        ],
                    }
                )
            )
        session.commit()
    return LoadCompetitionResponse(**response_dict)
