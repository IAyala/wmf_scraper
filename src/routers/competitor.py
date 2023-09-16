from parser.competitor import get_competitor_data
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_db
from models.competition import CompetitionModel

router = APIRouter()


@router.get(
    "/get_competitors_in_competition",
    summary="Add a new list of competitors taking part in a competition",
)
async def add_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[Dict]:
    try:
        result = session.exec(
            select(CompetitionModel).where(
                CompetitionModel.competition_id == competition_id
            )
        ).all()
        if result:
            return [x.dict() for x in get_competitor_data(result[0])]
        return []
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"{ex}") from ex
