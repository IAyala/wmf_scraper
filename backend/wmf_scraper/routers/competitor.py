from fastapi import APIRouter, Depends
from sqlmodel import Session, column, select

from wmf_scraper.actions.competition import the_competition
from wmf_scraper.actions.competitor import competitors_in_competition, preprocess_competitors
from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.database import get_db
from wmf_scraper.models.competitor import CompetitorModel, CountryModel
from wmf_scraper.parsers.competitor import get_competitor_data
from wmf_scraper.security import User, require_superadmin

router = APIRouter()


@router.get(
    "/get_competitors_in_competition",
    summary="Get competitors that take part in a competition",
)
@try_endpoint
async def get_competitors(competition_id: int, session: Session = Depends(get_db)) -> list[CompetitorModel]:
    competition = await the_competition(competition_id=competition_id, session=session)
    return competitors_in_competition(competition, session)


@router.get(
    "/get_competitors_in_competition_by_country",
    summary="Get competitors that take part in a competition that are from a certain country",
)
@try_endpoint
async def get_competitors_in_competition_by_country(
    competition_id: int, country_name: str, session: Session = Depends(get_db)
) -> list[CompetitorModel]:
    competition = await the_competition(competition_id=competition_id, session=session)
    return [c for c in competitors_in_competition(competition, session) if c.competitor_country == country_name]


@router.post(
    "/add_competitors_in_competition",
    summary="Add a new competitor",
)
@try_endpoint
async def add_competitors_in_competition(
    competition_id: int,
    session: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
) -> list[CompetitorModel]:
    competition_to_parse = await the_competition(competition_id=competition_id, session=session)
    competitors = get_competitor_data(competition_to_parse)
    return preprocess_competitors(competitors, session=session)


@router.get(
    "/get_countries_in_competition",
    summary="Which countries participate in a competition",
)
@try_endpoint
async def get_countries_in_competition(competition_id: int, session: Session = Depends(get_db)) -> list[CountryModel]:
    competition = await the_competition(competition_id=competition_id, session=session)
    competitors = competitors_in_competition(competition, session)
    return [CountryModel(competitor_country=c) for c in sorted({c.competitor_country for c in competitors})]


@router.get(
    "/get_competitors_by_name",
    summary="Gets the competitor details by name",
)
@try_endpoint
async def get_competitors_by_name(name: str, session: Session = Depends(get_db)) -> list[CompetitorModel]:
    return list(session.exec(select(CompetitorModel).where(column("competitor_name").contains(name))).all())


@router.get(
    "/get_competitors_by_country",
    summary="Gets the competitor details by country",
)
@try_endpoint
async def get_competitors_by_country(country: str, session: Session = Depends(get_db)) -> list[CompetitorModel]:
    return list(session.exec(select(CompetitorModel).where(column("competitor_country").contains(country))).all())
