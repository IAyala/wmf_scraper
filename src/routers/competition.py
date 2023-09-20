from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, column, select

from actions.competition import add_one_competition_helper
from actions.utils import try_endpoint
from database import get_db
from models.competition import CompetitionModel, CompetitionRequest

router = APIRouter()


@router.post("/add_one", summary="Add a new competition to the scraper")
@try_endpoint
async def add_one_competition(
    req: CompetitionRequest, session: Session = Depends(get_db)
) -> CompetitionModel:
    return await add_one_competition_helper(req=req, session=session)


@router.post("/add_many", summary="Add a list of new competitions to the scraper")
@try_endpoint
async def add_many_competitions(
    req: List[CompetitionRequest], session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    result = []
    for competition in req:
        result.append(
            await add_one_competition_helper(req=competition, session=session)
        )
    return result


@router.get("/get_all_competitions", summary="Gets the details for all competitions")
@try_endpoint
async def get_all_competitions(
    session: Session = Depends(get_db),
) -> List[CompetitionModel]:
    return session.exec(select(CompetitionModel)).all()


@router.get(
    "/get_competition_by_description",
    summary="Gets the competition details by description",
)
@try_endpoint
async def get_by_description(
    description: str, session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    return session.exec(
        select(CompetitionModel).where(column("description").contains(description))
    ).all()
