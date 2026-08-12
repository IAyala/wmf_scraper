import hashlib
import json
from datetime import datetime

from loguru import logger
from sqlmodel import Session, col, select

from wmf_scraper.actions.competition import remove_related_competition_objects, the_competition
from wmf_scraper.actions.competitor import competitors_mapping
from wmf_scraper.actions.utilities import optional_to_int_fallback_0
from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.load import LoadCompetitionResponse, LoadIncorrectTaskResponse
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel
from wmf_scraper.parsers.task import get_tasks_data
from wmf_scraper.parsers.task_results import (
    ParsedTask,
    competitors_for_competition,
    parse_tasks_parallel,
    resolve_task_results,
)


def fingerprint_fields(
    task: TaskModel, result: TaskResultModel | None, competitor: CompetitorModel | None
) -> list[str]:
    fields = [str(task.task_order), task.task_name, task.task_status, task.task_url]
    # A task with no result yet still counts: it disappearing is a change.
    if result is not None and competitor is not None:
        fields += [
            competitor.competitor_name,
            result.tr_result,
            str(result.tr_gross_score),
            str(result.tr_task_penalty),
            str(result.tr_competition_penalty),
            str(result.tr_net_score),
            result.tr_notes,
        ]
    return fields


def competition_fingerprint(competition_id: int, session: Session) -> str:
    """Hash everything a load rewrites, so before and after can be compared.

    Row ids are deliberately left out: a load deletes and re-inserts the tasks
    and their results, so the primary keys differ on every load even when the
    scraped data is identical.
    """
    rows = session.exec(
        select(TaskModel, TaskResultModel, CompetitorModel)
        .join(TaskResultModel, TaskResultModel.task_id == TaskModel.task_id, isouter=True)
        .join(CompetitorModel, CompetitorModel.competitor_id == TaskResultModel.competitor_id, isouter=True)
        .where(TaskModel.competition_id == competition_id)
    ).all()
    payload = sorted(fingerprint_fields(task, result, competitor) for task, result, competitor in rows)
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


async def update_load_time_and_purge_competition(competition_id: int, session: Session) -> CompetitionModel:
    my_competition = await the_competition(competition_id=competition_id, session=session)
    my_competition.competition_load_time = datetime.now()
    logger.debug(await remove_related_competition_objects(competition_id=competition_id, session=session))
    session.add(my_competition)
    return await the_competition(competition_id=competition_id, session=session)


async def load_tasks_and_competitors(competition: CompetitionModel, session: Session) -> tuple[list[ParsedTask], dict]:
    """Store the tasks, read every task page, then resolve the roster.

    The tasks are parsed before the competitors because they are the fallback
    source of the roster: an event whose tasks are all still provisional
    publishes results without ever publishing a competitor list.
    """
    for task in get_tasks_data(competition):
        session.add(task)
    tasks_list = session.exec(select(TaskModel).where(TaskModel.competition_id == competition.competition_id)).all()

    parsed_tasks = parse_tasks_parallel(list(tasks_list))
    competitors = competitors_for_competition(competition, parsed_tasks)
    return parsed_tasks, competitors_mapping(competitors=competitors, session=session)


async def load_task_results(
    parsed_tasks: list[ParsedTask], competitors: dict, session: Session
) -> dict[int, list[str]]:
    results, unmatched = resolve_task_results(parsed_tasks, competitors)
    for task_result in results:
        session.add(task_result)
    return unmatched


async def get_competitors_with_results(task_id: int, session: Session) -> set[str]:
    competitor_ids = session.exec(select(TaskResultModel.competitor_id).where(TaskResultModel.task_id == task_id)).all()
    competitor_names = session.exec(
        select(CompetitorModel.competitor_name).distinct().where(col(CompetitorModel.competitor_id).in_(competitor_ids))
    ).all()
    return set(competitor_names)


async def check_results_integrity(
    competition: CompetitionModel,
    competitors: dict,
    unmatched: dict[int, list[str]],
    session: Session,
) -> LoadCompetitionResponse:
    result = LoadCompetitionResponse(competition_loaded=competition)
    competitor_names = set(competitors.keys())
    task_list = session.exec(select(TaskModel).where(TaskModel.competition_id == competition.competition_id)).all()
    for task in task_list:
        task_id = optional_to_int_fallback_0(task.task_id)
        competitors_with_results = await get_competitors_with_results(task_id, session)
        # Results whose competitor could not be resolved were never stored, so
        # they can only be reported from what the parser handed back.
        result_no_competitor = sorted(set(unmatched.get(task_id, [])))
        competitor_no_result = sorted(competitor_names - competitors_with_results)

        if result_no_competitor or competitor_no_result:
            result.add_incorrect_task(
                LoadIncorrectTaskResponse(
                    task_order=task.task_order,
                    result_no_competitor=result_no_competitor,
                    competitor_no_result=competitor_no_result,
                )
            )
    return result


async def load_competition_helper(competition_id: int, session: Session) -> LoadCompetitionResponse:
    fingerprint_before = competition_fingerprint(competition_id=competition_id, session=session)
    updated_competition = await update_load_time_and_purge_competition(competition_id=competition_id, session=session)
    parsed_tasks, the_competitors = await load_tasks_and_competitors(competition=updated_competition, session=session)
    unmatched = await load_task_results(parsed_tasks, the_competitors, session)
    result = await check_results_integrity(updated_competition, the_competitors, unmatched, session)
    result.data_changed = competition_fingerprint(competition_id=competition_id, session=session) != fingerprint_before
    session.commit()
    return result
