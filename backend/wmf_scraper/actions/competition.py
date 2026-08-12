from sqlmodel import Session, select

from wmf_scraper.actions.utilities import exists_record
from wmf_scraper.models.competition import CompetitionModel, CompetitionPurgeResponse
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel


async def the_competition(competition_id: int, session: Session) -> CompetitionModel:
    query = select(CompetitionModel).where(CompetitionModel.competition_id == competition_id)
    if not exists_record(query=query, session=session):
        raise ValueError(f"Competition ID: {competition_id} not found")
    return session.exec(query).one()


async def add_one_competition_helper(
    competition_url: str, competition_description: str, session: Session
) -> CompetitionModel:
    to_add = CompetitionModel(competition_description=competition_description, competition_url=competition_url)
    session.add(to_add)
    session.commit()
    session.refresh(to_add)  # Refresh to get the auto-generated competition_id
    return to_add


async def remove_related_competition_objects(competition_id: int, session: Session) -> CompetitionPurgeResponse:
    n_tasks = n_task_results = 0
    for task in session.exec(select(TaskModel).where(TaskModel.competition_id == competition_id)).all():
        for task_result in session.exec(select(TaskResultModel).where(TaskResultModel.task_id == task.task_id)).all():
            session.delete(task_result)
            n_task_results += 1
        session.delete(task)
        n_tasks += 1
    return CompetitionPurgeResponse(
        competition_id_purged=competition_id,
        number_tasks_removed=n_tasks,
        number_task_results_removed=n_task_results,
    )


async def competitions_for_competitor(competitor_name: str, session: Session) -> list[CompetitionModel]:
    all_results = session.exec(
        select(CompetitionModel)
        .join(TaskModel, TaskModel.competition_id == CompetitionModel.competition_id)
        .join(
            TaskResultModel,
            TaskModel.task_id == TaskResultModel.task_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitorModel.competitor_name == competitor_name)
        .distinct()
    ).all()
    return list(all_results)
