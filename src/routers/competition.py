from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, column, select

from actions.competition import (
    add_one_competition_helper,
    remove_related_competition_objects,
    the_competition,
)
from actions.utilities import try_endpoint
from database import get_db
from models.competition import (
    CompetitionModel,
    CompetitionPurgeResponse,
    CompetitionRequest,
)

router = APIRouter()


@router.post("/add_one", summary="Add a new competition to the scraper")
@try_endpoint
async def add_one(
    competition_description: str,
    competition_url: str,
    session: Session = Depends(get_db),
) -> CompetitionModel:
    return await add_one_competition_helper(
        competition_description=competition_description,
        competition_url=competition_url,
        session=session,
    )


@router.post("/add_many", summary="Add a list of new competitions to the scraper")
@try_endpoint
async def add_many(
    req: List[CompetitionRequest], session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    result = []
    for elem in req:
        result.append(
            await add_one_competition_helper(
                competition_description=elem.competition_description,
                competition_url=elem.competition_url,
                session=session,
            )
        )
    return result


@router.post("/remove_one", summary="Remove one competition to the scraper")
@try_endpoint
async def remove_one(
    competition_id: int, session: Session = Depends(get_db)
) -> CompetitionPurgeResponse:
    competition_to_remove = await the_competition(
        competition_id=competition_id, session=session
    )
    result = await remove_related_competition_objects(
        competition_id=competition_id, session=session
    )
    session.delete(competition_to_remove)
    session.commit()
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
async def get_competition_by_description(
    description: str, session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    return session.exec(
        select(CompetitionModel).where(
            column("competition_description").contains(description)
        )
    ).all()
