from sqlmodel import Session, func, select

from actions.utils import exists_record
from models.competition import CompetitionModel


async def next_competition_id(competition_id: int, session: Session) -> int:
    the_query = select(CompetitionModel).where(
        CompetitionModel.competition_id == competition_id
    )
    if not exists_record(the_query, session=session):
        result = session.execute(
            select([func.count(CompetitionModel.competition_id)])
        ).scalar()
        return int(result) + 1  # type: ignore
    raise ValueError(f"Competition id: {competition_id} already exists in database...")
