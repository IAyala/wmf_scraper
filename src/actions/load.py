from datetime import datetime
from parser.competitor import get_competitor_data
from parser.task import get_tasks_data
from parser.task_results import get_task_results_parallel
from typing import List, Set, Tuple

from loguru import logger
from sqlmodel import Session, col, select

from actions.competition import remove_related_competition_objects, the_competition
from actions.competitor import competitors_mapping
from actions.utilities import optional_to_int_fallback_0
from models.competition import CompetitionModel
from models.competitor import CompetitorModel
from models.load import LoadCompetitionResponse, LoadIncorrectTaskResponse
from models.task import TaskModel
from models.task_result import TaskResultModel


async def update_load_time_and_purge_competition(
    competition_id: int, session: Session
) -> CompetitionModel:
    my_competition = await the_competition(
        competition_id=competition_id, session=session
    )
    my_competition.competition_load_time = datetime.now()
    logger.debug(
        await remove_related_competition_objects(
            competition_id=competition_id, session=session
        )
    )
    session.add(my_competition)
    return await the_competition(competition_id=competition_id, session=session)


async def load_tasks_and_competitors(
    competition: CompetitionModel, session: Session
) -> Tuple[List[TaskModel], dict]:
    the_competitors = competitors_mapping(
        competitors=get_competitor_data(competition), session=session
    )

    for task in get_tasks_data(competition):
        session.add(task)
    tasks_list = session.exec(
        select(TaskModel).where(TaskModel.competition_id == competition.competition_id)
    ).all()

    return tasks_list, the_competitors


async def load_task_results(
    tasks: List[TaskModel], competitors: dict, session: Session
) -> None:
    for task_result in get_task_results_parallel(tasks, competitors):
        session.add(task_result)


async def get_competitors_with_results(task_id: int, session: Session) -> Set[str]:
    competitor_ids = session.exec(
        select(TaskResultModel.competitor_id).where(TaskResultModel.task_id == task_id)
    ).all()
    competitor_names = session.exec(
        select(CompetitorModel.competitor_name)
        .distinct()
        .where(col(CompetitorModel.competitor_id).in_(competitor_ids))
    ).all()
    return set(competitor_names)


async def check_results_integrity(
    competition: CompetitionModel, competitors: dict, session: Session
) -> LoadCompetitionResponse:
    result = LoadCompetitionResponse(competition_loaded=competition)
    competitor_names = set(competitors.keys())
    task_list = session.exec(
        select(TaskModel).where(TaskModel.competition_id == competition.competition_id)
    ).all()
    for task in task_list:
        result_no_competitor = competitor_no_result = []
        competitors_with_results = await get_competitors_with_results(
            optional_to_int_fallback_0(task.task_id), session
        )
        if competitors_with_results - competitor_names:
            result_no_competitor = list(competitors_with_results - competitor_names)
        if competitor_names - competitors_with_results:
            competitor_no_result = list(competitor_names - competitors_with_results)

        if result_no_competitor or competitor_no_result:
            result.add_incorrect_task(
                LoadIncorrectTaskResponse(
                    task_order=task.task_order,
                    result_no_competitor=result_no_competitor,
                    competitor_no_result=competitor_no_result,
                )
            )
    return result


async def load_competition_helper(
    competition_id: int, session: Session
) -> LoadCompetitionResponse:
    updated_competition = await update_load_time_and_purge_competition(
        competition_id=competition_id, session=session
    )
    tasks, the_competitors = await load_tasks_and_competitors(
        competition=updated_competition, session=session
    )
    await load_task_results(tasks, the_competitors, session)
    result = await check_results_integrity(
        updated_competition, the_competitors, session
    )
    session.commit()
    return result
