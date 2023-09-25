from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlmodel import Session, column, select

from actions.competition import add_one_competition_helper
from actions.load.competition import remove_related_competition_objects
from actions.utils import exists_record, try_endpoint
from database import get_db
from models.competition import CompetitionModel, CompetitionRequest

router = APIRouter()


@router.post("/add_one", summary="Add a new competition to the scraper")
@try_endpoint
async def add_one_competition(
    req: CompetitionRequest, session: Session = Depends(get_db)
) -> CompetitionModel:
    return await add_one_competition_helper(req=req, session=session)


@router.post("/add_many", summary="Add a list of new competitions to the scraper")
@try_endpoint
async def add_many_competitions(
    req: List[CompetitionRequest], session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    result = []
    for competition in req:
        result.append(
            await add_one_competition_helper(req=competition, session=session)
        )
    return result


@router.post("/remove_one", summary="Remove one competition to the scraper")
@try_endpoint
async def remove_one_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> Dict:
    if exists_record(
        select(CompetitionModel).where(
            CompetitionModel.competition_id == competition_id
        ),
        session=session,
    ):
        competition = session.exec(
            select(CompetitionModel).where(
                CompetitionModel.competition_id == competition_id
            )
        ).one()
        session.delete(competition)
        n_tasks, n_task_results = await remove_related_competition_objects(
            competition_id=competition_id, session=session
        )
        session.commit()
        return {
            "status": f"Competition {competition_id} successfully removed. {n_tasks} Tasks removed and {n_task_results} TaskResults removed"
        }
    return {"status": f"Competition {competition_id} does not exist"}


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
async def get_by_description(
    description: str, session: Session = Depends(get_db)
) -> List[CompetitionModel]:
    return session.exec(
        select(CompetitionModel).where(column("description").contains(description))
    ).all()
