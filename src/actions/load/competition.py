from datetime import datetime

from sqlmodel import Session

from actions.competition import the_competition
from actions.load.competitors import load_competitors_for_competition
from actions.load.task_results import load_task_results_for_competition
from actions.load.tasks import load_tasks_for_competition
from models.load import (
    LoadCompetitionRequest,
    LoadCompetitionResponse,
    LoadCompetitionTaskResultsResponse,
)
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
        response_dict = {
            "competition_loaded": competition_to_update.dict(),
            "tasks_loaded": [],
        }
        tasks_added = await load_tasks_for_competition(
            competition_to_update, session=session
        )
        await load_competitors_for_competition(competition_to_update, session=session)
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
