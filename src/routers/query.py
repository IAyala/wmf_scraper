from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from actions.competition import the_competition
from actions.utils import try_endpoint
from database import get_db
from models.query import CompetitorResults
from models.task_result import TaskResultModel

router = APIRouter()


@router.get(
    "/results_competitor_in_competition",
    summary="Load Results for a Competitor in a Competition",
)
@try_endpoint
async def add_one_competition(
    competition_id: int, competitor_name: str, session: Session = Depends(get_db)
) -> List[CompetitorResults]:
    result = []
    this_competition = await the_competition(
        competition_id=competition_id, session=session
    )
    for task in this_competition.tasks:
        result_for_competitor = list(
            filter(lambda x: competitor_name in x.competitor_name, task.task_results)
        )
        if len(result_for_competitor) != 1:
            if len(result_for_competitor) == 0:
                message = f"Competition {this_competition.description} does not have results for {competitor_name} in task {task.task_order}. "
                competitors_here = (
                    session.execute(
                        select(TaskResultModel.competitor_name)
                        .where(TaskResultModel.competition_id == competition_id)
                        .distinct()
                    )
                    .scalars()
                    .all()
                )
                message += f"Competitors in this competitions are: {competitors_here}"
                raise ValueError(message)
            else:
                competitors = [x.competitor_name for x in result_for_competitor]
                raise ValueError(
                    f"Competition {competition_id} does have results for more than one competitor: {competitors}"
                )
        my_result: TaskResultModel = result_for_competitor[0]
        result.append(
            CompetitorResults(
                result=my_result.result,
                gross_score=my_result.gross_score,
                task_penalty=my_result.task_penalty,
                competition_penalty=my_result.competition_penalty,
                net_score=my_result.net_score,
                notes=my_result.notes,
                competitor_name=my_result.competitor_name,
                competition_name=this_competition.description,
                task_order=task.task_order,
                task_name=task.name,
                task_status=task.status,
            )
        )
    return sorted(result, key=lambda x: x.task_order)
