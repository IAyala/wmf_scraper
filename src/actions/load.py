from parser.task import get_tasks_data
from parser.task_results import get_task_results
from typing import List

from sqlmodel import Session, select

from models.competition import CompetitionModel
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
