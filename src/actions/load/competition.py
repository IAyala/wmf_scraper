from datetime import datetime
from typing import Tuple

from sqlmodel import Session, select

from actions.competition import the_competition
from actions.load.competitors import load_competitors_for_competition
from actions.load.task_results import load_task_results_for_competition
from actions.load.tasks import load_tasks_for_competition
from actions.load.utilities import get_load_results_response
from models.load import LoadCompetitionRequest, LoadCompetitionResponse
from models.task import TaskModel
from models.task_result import TaskResultModel


async def load_competition_helper(
    req: LoadCompetitionRequest, session: Session
) -> LoadCompetitionResponse:
    with session.begin():
        competition_to_update = await the_competition(
            req.competition_id, session=session
        )
        competition_to_update.load_time = datetime.now()
        await remove_related_competition_objects(req.competition_id, session)
        result = LoadCompetitionResponse(competition_loaded=competition_to_update)
        competitor_names = await load_competitors_for_competition(
            competition_to_update, session=session
        )

        for task_to_add in await load_tasks_for_competition(
            competition_to_update, session=session
        ):
            result.tasks_loaded.append(
                get_load_results_response(
                    await load_task_results_for_competition(
                        competition_to_update, task_to_add, session=session
                    ),
                    competitor_names,
                    task_to_add,
                )
            )
        if any([x.load_message != "OK" for x in result.tasks_loaded]):
            result.status = "ERROR!!"
        session.commit()
    return result


async def remove_related_competition_objects(
    competition_id: int, session: Session
) -> Tuple[int, int]:
    n_tasks = n_task_results = 0
    for task in session.exec(
        select(TaskModel).where(TaskModel.competition_id == competition_id)
    ).all():
        session.delete(task)
        n_tasks += 1
    for task_result in session.exec(
        select(TaskResultModel).where(TaskResultModel.competition_id == competition_id)
    ).all():
        session.delete(task_result)
        n_task_results += 1
    return (n_tasks, n_task_results)
