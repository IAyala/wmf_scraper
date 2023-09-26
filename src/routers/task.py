# from parser.task import get_tasks_data
# from typing import List

# from fastapi import APIRouter, Depends
# from sqlmodel import Session, select

# from actions.utils import try_endpoint
# from database import get_db
# from models.competition import CompetitionModel
# from models.task import TaskModel

# router = APIRouter()


# @router.get(
#     "/get_tasks_for_competition", summary="Add a new competition to the scraper"
# )
# @try_endpoint
# async def get_tasks_for_competition(
#     competition_id: int, session: Session = Depends(get_db)
# ) -> List[TaskModel]:
#     result = session.exec(
#         select(CompetitionModel).where(
#             CompetitionModel.competition_id == competition_id
#         )
#     ).all()
#     if result:
#         return get_tasks_data(result[0])
#     return []
