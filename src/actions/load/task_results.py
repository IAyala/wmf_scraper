from parser.task_results import get_task_results
from typing import List

from sqlmodel import Session, select

from models.competition import CompetitionModel
from models.competitor import CompetitorModel
from models.task import TaskModel
from models.task_result import TaskResultModel


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
            competitor_id = session.exec(
                select(CompetitorModel.competitor_id).where(
                    CompetitorModel.name == updated_task_result.competitor_name
                )
            ).first()
            updated_task_result.competitor_id = competitor_id
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
