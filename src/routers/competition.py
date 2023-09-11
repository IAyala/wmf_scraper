from typing import Dict

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, func, select

from database.db_engine import engine
from models.competition import CompetitionModel, CompetitionRequest

router = APIRouter()


async def how_many_competitions(session) -> int:
    result = session.exec(select([func.count(CompetitionModel.competition_id)])).one()
    return result  # type: ignore


@router.post("/add", summary="Add a new competition to the scraper")
async def add_competition(req: CompetitionRequest) -> Dict:
    with Session(engine) as session:
        num_prev_competitions = await how_many_competitions(session)
        try:
            to_add = CompetitionModel(**req.dict())
            to_add.competition_id = num_prev_competitions + 1
            session.add(to_add)
            session.commit()
            return dict(req.dict(), **{"competition_id": num_prev_competitions + 1})
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"{ex}") from ex
