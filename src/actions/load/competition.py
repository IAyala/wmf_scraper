from datetime import datetime

from sqlmodel import Session

from actions.competition import the_competition
from actions.load.competitors import load_competitors_for_competition
from actions.load.task_results import load_task_results_for_competition
from actions.load.tasks import load_tasks_for_competition
from actions.load.utilities import get_load_results_response
from models.load import LoadCompetitionRequest, LoadCompetitionResponse


async def load_competition_helper(
    req: LoadCompetitionRequest, session: Session
) -> LoadCompetitionResponse:
    with session.begin():
        competition_to_update = await the_competition(
            req.competition_id, session=session
        )
        competition_to_update.load_time = datetime.now()
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
