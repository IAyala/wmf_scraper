from sqlmodel import Session

from actions.competition import the_competition
from models.load import LoadCompetitionResponse

# TODO:
# - First remove all related competition objects (should be just calling a method)
# - Then add competition
# - Then add tasks and competitors (this is fast and requires reading same url)
# - Then, in parallel, retrieve task results (for each task we have to read a different url) and after retrieving the write (session cannot be serialized)

# All the code should be in actions.load, remove the folder
# Add tests for loading, can be challenging as for each result we need a different html file


async def load_competition_helper(
    competition_id: int, session: Session
) -> LoadCompetitionResponse:
    my_competition = the_competition(competition_id=competition_id, session=session)
    return LoadCompetitionResponse(competition_loaded=my_competition)
    # with session.begin():
    #     competition_to_update = await the_competition(
    #         req.competition_id, session=session
    #     )
    #     competition_to_update.load_time = datetime.now()
    #     await remove_related_competition_objects(req.competition_id, session)
    #     result = LoadCompetitionResponse(competition_loaded=competition_to_update)
    #     competitor_names = await load_competitors_for_competition(
    #         competition_to_update, session=session
    #     )

    #     for task_to_add in await load_tasks_for_competition(
    #         competition_to_update, session=session
    #     ):
    #         result.tasks_loaded.append(
    #             get_load_results_response(
    #                 await load_task_results_for_competition(
    #                     competition_to_update, task_to_add, session=session
    #                 ),
    #                 competitor_names,
    #                 task_to_add,
    #             )
    #         )
    #     if any([x.load_message != "OK" for x in result.tasks_loaded]):
    #         result.status = "ERROR!!"
    #     session.commit()
    # return result
