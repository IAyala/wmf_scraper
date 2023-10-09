from typing import List, Optional

from sqlmodel import Session, col, func, select

from models.competition import CompetitionModel
from models.competitor import CompetitorModel
from models.query import (
    CompetitionOverall,
    CompetitionOverallWithPosition,
    CompetitorOverallByTask,
    CompetitorResults,
    CountryResults,
    CountryResultsWithPosition,
)
from models.task import TaskModel
from models.task_result import TaskResultModel


def query_overalls(competition_id: int):
    return (
        select(
            CompetitorModel.competitor_name,
            CompetitorModel.competitor_country,
            func.sum(TaskResultModel.tr_net_score).label("total_score"),  # type: ignore
            func.sum(TaskResultModel.tr_competition_penalty).label(
                "total_competition_penalty"
            ),  # type: ignore
            func.sum(TaskResultModel.tr_task_penalty).label(
                "total_task_penalty"
            ),  # type: ignore
            func.count(TaskResultModel.task_id).label("number_tasks"),  # type: ignore
        )
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .group_by(CompetitorModel.competitor_name)
    )


def query_average_by_country(competition_id: int, session: Session):
    competitors_in_first_task = (
        select(TaskResultModel.competitor_id)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .where(TaskModel.task_order == 1)
        .subquery()
    )

    competitors_per_country = (
        select(
            CompetitorModel.competitor_country,
            func.count(CompetitorModel.competitor_id).label("number_competitors"),  # type: ignore
        )
        .join(
            competitors_in_first_task,
            competitors_in_first_task.c.competitor_id == CompetitorModel.competitor_id,
        )
        .group_by(CompetitorModel.competitor_country)
        .subquery()
    )

    return (
        select(
            CompetitorModel.competitor_country,
            func.sum(TaskResultModel.tr_net_score).label("total_score"),  # type: ignore
            func.count(TaskResultModel.task_id).label("number_tasks"),  # type: ignore
            competitors_per_country.c.number_competitors,
        )
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .join(
            competitors_per_country,
            competitors_per_country.c.competitor_country
            == CompetitorModel.competitor_country,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .group_by(CompetitorModel.competitor_country)
    )


def query_overalls_up_to_task(competition_id: int, up_to_task: int):
    return query_overalls(competition_id).where(TaskModel.task_order <= up_to_task)


async def query_result_for_competitor_in_competition(
    competition_id: int, competitor_name: str, session: Session
) -> List[CompetitorResults]:
    all_results = session.exec(
        select(TaskResultModel, TaskModel, CompetitorModel, CompetitionModel)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .where(col(CompetitorModel.competitor_name).contains(competitor_name))
    ).all()
    return [
        CompetitorResults(
            result=task_result.tr_result,
            gross_score=task_result.tr_gross_score,
            task_penalty=task_result.tr_task_penalty,
            competition_penalty=task_result.tr_competition_penalty,
            net_score=task_result.tr_net_score,
            notes=task_result.tr_notes,
            competitor_name=competitor.competitor_name,
            competitor_country=competitor.competitor_country,
            competition_name=competition.competition_description,
            task_order=task.task_order,
            task_name=task.task_name,
            task_status=task.task_status,
        )
        for task_result, task, competitor, competition in all_results
    ]


async def query_country_results_for_competition(
    competition_id: int, session: Session
) -> List[CountryResultsWithPosition]:
    result = []
    all_results = session.exec(
        query_average_by_country(competition_id=competition_id, session=session)
    ).all()
    for elem in all_results:
        result.append(
            CountryResults(
                competitor_country=elem.competitor_country,
                number_competitors=elem.number_competitors,
                average_score=round(elem.total_score / elem.number_tasks, 2),
            )
        )
    return [
        CountryResultsWithPosition(**res.dict(), position=pos + 1)
        for pos, res in enumerate(
            sorted(result, key=lambda x: x.average_score, reverse=True)
        )
    ]


async def query_overall_results_for_competition(
    competition_id: int, session: Session, up_to_task: Optional[int] = None
) -> List[CompetitionOverallWithPosition]:
    result = []
    if up_to_task:
        all_results = session.exec(
            query_overalls_up_to_task(competition_id, up_to_task)
        ).all()
    else:
        all_results = session.exec(query_overalls(competition_id)).all()
    for elem in all_results:
        result.append(
            CompetitionOverall(
                total_score=elem.total_score,
                average_score=round(elem.total_score / elem.number_tasks, 2),
                total_competition_penalty=elem.total_competition_penalty,
                total_task_penalty=elem.total_task_penalty,
                competitor_name=elem.competitor_name,
                competitor_country=elem.competitor_country,
            )
        )
    return [
        CompetitionOverallWithPosition(**res.dict(), position=pos + 1)
        for pos, res in enumerate(
            sorted(result, key=lambda x: x.total_score, reverse=True)
        )
    ]


async def query_positions_by_competitor_in_competition(
    competition_id: int, competitor_name: str, session: Session
) -> CompetitorOverallByTask:
    num_tasks = session.exec(
        select(
            func.count(TaskModel.task_id).label("number_tasks")  # type:ignore
        )
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
    ).first()
    competitor = session.exec(
        select(CompetitorModel).where(
            CompetitorModel.competitor_name == competitor_name
        )
    ).one_or_none()
    if num_tasks and num_tasks > 0 and competitor:
        result = CompetitorOverallByTask(**competitor.dict())
        for i in range(1, num_tasks + 1):
            results_up_to_task_i = await query_overall_results_for_competition(
                competition_id=competition_id, session=session, up_to_task=i
            )
            my_competitor_position = next(
                filter(
                    lambda x: x.competitor_name == competitor_name, results_up_to_task_i
                )
            )
            result.competitor_positions.append(my_competitor_position.position)
        return result
    raise ValueError(
        f"Competition with id {competition_id} does not exist, or competitor {competitor_name} does not exist..."
    )
