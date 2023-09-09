from typing import Dict

from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from database.db_engine import engine
from models.competition import CompetitionModel, CompetitionRequest

router = APIRouter()


@router.post("/add", summary="Add a new competition to the scraper")
async def add_competition(req: CompetitionRequest) -> Dict[str, str]:
    try:
        with Session(engine) as session:
            session.add(CompetitionModel(**req.dict()))
            session.commit()
        return req.dict()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"{ex}") from ex
