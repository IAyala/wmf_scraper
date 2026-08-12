from loguru import logger
from sqlmodel import Session, select

from wmf_scraper.actions.utilities import exists_record
from wmf_scraper.models.competitor import CompetitorModel


def preprocess_competitors(competitors: list[CompetitorModel], session: Session) -> list[CompetitorModel]:
    result = []
    for competitor in competitors:
        query = select(CompetitorModel).where(CompetitorModel.competitor_name == competitor.competitor_name)
        if not exists_record(query=query, session=session):
            session.add(competitor)
            updated_competitor = session.exec(query).one()
            logger.debug(
                f"Competitor {updated_competitor.competitor_id} added: "
                f"{competitor.competitor_name.strip()} from {competitor.competitor_country}"
            )
        else:
            updated_competitor = session.exec(query).one()
        result.append(updated_competitor)
        session.commit()
    return result


def competitors_mapping(competitors: list[CompetitorModel], session: Session) -> dict:
    result = {}
    for competitor in preprocess_competitors(competitors, session):
        result[competitor.competitor_name] = competitor.competitor_id
    return result
