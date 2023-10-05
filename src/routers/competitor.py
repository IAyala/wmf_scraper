from parser.competitor import get_competitor_data
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, column, select

from actions.competition import the_competition
from actions.competitor import preprocess_competitors
from actions.utilities import try_endpoint
from database import get_db
from models.competitor import CompetitorModel, CountryModel

router = APIRouter()


@router.get(
    "/get_competitors_in_competition",
    summary="Get competitors that take part in a competition",
)
@try_endpoint
async def get_competitors(
    competition_id: int, session: Session = Depends(get_db)
) -> List[CompetitorModel]:
    competition_to_parse = await the_competition(
        competition_id=competition_id, session=session
    )
    return get_competitor_data(competition_to_parse)


@router.post(
    "/add_competitors_in_competition",
    summary="Add a new competitor",
)
@try_endpoint
async def add_competitors_in_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[CompetitorModel]:
    competition_to_parse = await the_competition(
        competition_id=competition_id, session=session
    )
    competitors = get_competitor_data(competition_to_parse)
    return preprocess_competitors(competitors, session=session)


@router.get(
    "/get_countries_in_competition",
    summary="Which countries participate in a competition",
)
@try_endpoint
async def get_countries_in_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> List[CountryModel]:
    competition_to_parse = await the_competition(
        competition_id=competition_id, session=session
    )
    competitors = get_competitor_data(competition_to_parse)
    return [
        CountryModel(competitor_country=x)
        for x in list(set([x.competitor_country for x in competitors]))
    ]


@router.get(
    "/get_competitors_by_name",
    summary="Gets the competitor details by name",
)
@try_endpoint
async def get_competitors_by_name(
    name: str, session: Session = Depends(get_db)
) -> List[CompetitorModel]:
    return session.exec(
        select(CompetitorModel).where(column("competitor_name").contains(name))
    ).all()


@router.get(
    "/get_competitors_by_country",
    summary="Gets the competitor details by country",
)
@try_endpoint
async def get_competitors_by_country(
    country: str, session: Session = Depends(get_db)
) -> List[CompetitorModel]:
    return session.exec(
        select(CompetitorModel).where(column("competitor_country").contains(country))
    ).all()
