from typing import List

from sqlmodel import Session, col, func, select

from models.competition import CompetitionModel
from models.competitor import CompetitorModel
from models.query import CompetitionOverall, CompetitorResults
from models.task import TaskModel
from models.task_result import TaskResultModel


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
            result=x[0].tr_result,
            gross_score=x[0].tr_gross_score,
            task_penalty=x[0].tr_task_penalty,
            competition_penalty=x[0].tr_competition_penalty,
            net_score=x[0].tr_net_score,
            notes=x[0].tr_notes,
            competitor_name=x[2].competitor_name,
            competitor_country=x[2].competitor_country,
            competition_name=x[3].competition_description,
            task_order=x[1].task_order,
            task_name=x[1].task_name,
            task_status=x[1].task_status,
        )
        for x in all_results
    ]


async def query_overall_results_for_competition(
    competition_id: int, session: Session
) -> List[CompetitionOverall]:
    result = []
    all_results = session.exec(
        select(
            CompetitorModel.competitor_name,
            CompetitorModel.competitor_country,
            func.sum(TaskResultModel.tr_net_score).label("total_score"),  # type: ignore
            func.sum(TaskResultModel.tr_competition_penalty).label("total_competition_penalty"),  # type: ignore
            func.sum(TaskResultModel.tr_task_penalty).label("total_task_penalty"),  # type: ignore
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
    ).all()
    for elem in all_results:
        result.append(
            CompetitionOverall(
                total_score=elem.total_score,
                total_competition_penalty=elem.total_competition_penalty,
                total_task_penalty=elem.total_task_penalty,
                competitor_name=elem.competitor_name,
                competitor_country=elem.competitor_country,
            )
        )
    return sorted(result, key=lambda x: x.total_score, reverse=True)
