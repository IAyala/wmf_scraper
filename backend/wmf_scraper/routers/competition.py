from fastapi import APIRouter, Depends
from sqlmodel import Session, col, select

from wmf_scraper.actions.competition import (
    add_one_competition_helper,
    competitions_for_competitor,
    remove_related_competition_objects,
    the_competition,
    update_one_competition_helper,
)
from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.database import get_db
from wmf_scraper.models.competition import (
    CompetitionModel,
    CompetitionPurgeResponse,
    CompetitionRequest,
)
from wmf_scraper.security import User, require_superadmin

router = APIRouter()


@router.post("/add_one", summary="Add a new competition to the scraper")
@try_endpoint
async def add_one(
    competition_description: str,
    competition_url: str,
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> CompetitionModel:
    return await add_one_competition_helper(
        competition_description=competition_description,
        competition_url=competition_url,
        session=session,
    )


@router.post("/add_many", summary="Add a list of new competitions to the scraper")
@try_endpoint
async def add_many(
    req: list[CompetitionRequest],
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> list[CompetitionModel]:
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


@router.post("/update_one", summary="Update a competition's description and URL")
@try_endpoint
async def update_one(
    competition_id: int,
    req: CompetitionRequest,
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> CompetitionModel:
    return await update_one_competition_helper(
        competition_id=competition_id,
        competition_description=req.competition_description,
        competition_url=req.competition_url,
        session=session,
    )


@router.post("/remove_one", summary="Remove a competition and everything loaded for it")
@try_endpoint
async def remove_one(
    competition_id: int,
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> CompetitionPurgeResponse:
    competition_to_remove = await the_competition(competition_id=competition_id, session=session)
    result = await remove_related_competition_objects(competition_id=competition_id, session=session)
    session.delete(competition_to_remove)
    session.commit()
    return result


@router.get("/get_all_competitions", summary="Gets the details for all competitions")
@try_endpoint
async def get_all_competitions(
    session: Session = Depends(get_db),
) -> list[CompetitionModel]:
    return list(session.exec(select(CompetitionModel)).all())


@router.get(
    "/get_competition_by_description",
    summary="Gets the competition details by description",
)
@try_endpoint
async def get_competition_by_description(
    description: str, session: Session = Depends(get_db)
) -> list[CompetitionModel]:
    return list(
        session.exec(
            select(CompetitionModel).where(col(CompetitionModel.competition_description).contains(description))
        ).all()
    )


@router.get(
    "/get_competitions_for_competitor",
    summary="Gets the competitions where a competitor has taken part",
)
@try_endpoint
async def get_competitions_for_competitor(
    competitor_name: str, session: Session = Depends(get_db)
) -> list[CompetitionModel]:
    return await competitions_for_competitor(competitor_name, session)
