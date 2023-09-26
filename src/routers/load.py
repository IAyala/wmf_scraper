# from typing import List

# from fastapi import APIRouter, Depends
# from sqlmodel import Session

# from actions.load.competition import load_competition_helper
# from actions.utils import try_endpoint
# from database import get_db
# from models.load import LoadCompetitionRequest, LoadCompetitionResponse

# router = APIRouter()


# @router.post("/load_competition", summary="Load Competition Results")
# @try_endpoint
# async def load_competition(
#     req: LoadCompetitionRequest, session: Session = Depends(get_db)
# ) -> LoadCompetitionResponse:
#     return await load_competition_helper(req=req, session=session)


# @router.post("/load_many_competitions", summary="Load Competition Results")
# @try_endpoint
# async def load_many_competitions(
#     req: List[LoadCompetitionRequest], session: Session = Depends(get_db)
# ) -> List[LoadCompetitionResponse]:
#     result = []
#     for elem in req:
#         result.append(await load_competition_helper(elem, session=session))
#     return result
