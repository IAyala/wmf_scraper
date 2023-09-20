from sqlmodel import Session, select

from models.competition import CompetitionModel, CompetitionRequest


async def the_competition(competition_id: int, session: Session) -> CompetitionModel:
    the_competition = session.exec(
        select(CompetitionModel).where(
            CompetitionModel.competition_id == competition_id
        )
    ).one_or_none()
    if not the_competition:
        raise ValueError(f"Competition ID: {competition_id} not found")
    return the_competition


async def add_one_competition_helper(
    req: CompetitionRequest, session: Session
) -> CompetitionModel:
    to_add = CompetitionModel(**req.dict())
    session.add(to_add)
    session.commit()
    return to_add
