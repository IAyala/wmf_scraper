from typing import List

from loguru import logger
from sqlmodel import Session, select

from actions.utilities import exists_record
from models.competitor import CompetitorModel


def preprocess_competitors(
    competitors: List[CompetitorModel], session: Session
) -> List[CompetitorModel]:
    result = []
    for competitor in competitors:
        query = select(CompetitorModel).where(
            CompetitorModel.competitor_name == competitor.competitor_name
        )
        if not exists_record(query=query, session=session):
            session.add(competitor)
            updated_competitor = session.exec(query).one()
            logger.debug(
                f"Competitor {updated_competitor.competitor_id} added: {competitor.competitor_name.strip()} from {competitor.competitor_country}"
            )
        else:
            updated_competitor = session.exec(query).one()
        result.append(updated_competitor)
        session.commit()
    return result


def competitors_mapping(competitors: List[CompetitorModel], session: Session) -> dict:
    result = {}
    for competitor in preprocess_competitors(competitors, session):
        result[competitor.competitor_name] = competitor.competitor_id
    return result
