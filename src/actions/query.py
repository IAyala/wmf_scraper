from typing import List

from sqlmodel import Session, col, select

from models.competition import CompetitionModel
from models.competitor import CompetitorModel
from models.query import CompetitorResults
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
