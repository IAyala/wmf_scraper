from loguru import logger
from sqlmodel import Session, col, select

from wmf_scraper.actions.utilities import exists_record
from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel
from wmf_scraper.parsers.competitor import get_competitor_data


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


def stored_competitors_in_competition(competition_id: int, session: Session) -> list[CompetitorModel]:
    """Competitors that have at least one stored result in this competition."""
    query = (
        select(CompetitorModel)
        .join(TaskResultModel, TaskResultModel.competitor_id == CompetitorModel.competitor_id)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .where(TaskModel.competition_id == competition_id)
        .distinct()
        .order_by(col(CompetitorModel.competitor_name))
    )
    return list(session.exec(query).all())


def competitors_in_competition(competition: CompetitionModel, session: Session) -> list[CompetitorModel]:
    """The roster to show for a competition.

    Prefers what has been loaded into the database, because that is what the
    results screens can actually display, and because WatchMeFly only publishes
    the standings table once an event has official results — scraping it for an
    event still in progress returns nothing. Falls back to the live page so a
    competition that has been added but not loaded yet still lists its pilots.
    """
    stored = stored_competitors_in_competition(competition.competition_id or 0, session)
    if stored:
        return stored
    return sorted(get_competitor_data(competition), key=lambda c: c.competitor_name)
