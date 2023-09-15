from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, column, func, select

from database import get_db
from models.competition import CompetitionModel, CompetitionRequest

router = APIRouter()


async def how_many_competitions(session: Session) -> int:
    result = session.exec(select([func.count(CompetitionModel.competition_id)])).one()
    return result  # type: ignore


@router.post("/add", summary="Add a new competition to the scraper")
async def add_competition(
    req: CompetitionRequest, session: Session = Depends(get_db)
) -> Dict:
    num_prev_competitions = await how_many_competitions(session)
    try:
        to_add = CompetitionModel(**req.dict())
        to_add.competition_id = num_prev_competitions + 1
        session.add(to_add)
        session.commit()
        return dict(req.dict(), **{"competition_id": num_prev_competitions + 1})
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"{ex}") from ex


@router.get(
    "/get_by_description", summary="Gets the competition details by description"
)
async def get_by_description(
    description: str, session: Session = Depends(get_db)
) -> List[Dict]:
    return [
        x.dict()
        for x in session.exec(
            select(CompetitionModel).where(column("description").contains(description))
        )
    ]


@router.get("/all", summary="Gets the competition details by description")
async def get_all_competitions(session: Session = Depends(get_db)) -> List[Dict]:
    return [x.dict() for x in session.exec(select(CompetitionModel))]
