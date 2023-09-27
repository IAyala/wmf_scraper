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
                f"Competitor {updated_competitor.competitor_id} added: {updated_competitor.competitor_name} from {updated_competitor.competitor_country}"
            )
        else:
            updated_competitor = session.exec(query).one()
        result.append(updated_competitor)
        session.commit()
    return result
