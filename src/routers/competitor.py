# from parser.competitor import get_competitor_data
# from typing import List

# from fastapi import APIRouter, Depends
# from sqlmodel import Session, select

# from actions.utils import try_endpoint
# from database import get_db
# from models.competition import CompetitionModel
# from models.competitor import CompetitorSimpleModel

# router = APIRouter()


# @router.get(
#     "/get_competitors_in_competition",
#     summary="Add a new list of competitors taking part in a competition",
# )
# @try_endpoint
# async def get_competitors(
#     competition_id: int, session: Session = Depends(get_db)
# ) -> List[CompetitorSimpleModel]:
#     result = session.exec(
#         select(CompetitionModel).where(
#             CompetitionModel.competition_id == competition_id
#         )
#     ).all()
#     if result:
#         return get_competitor_data(result[0])
#     return []
