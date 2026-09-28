from fastapi import APIRouter, Depends
from sqlmodel import Session

from wmf_scraper.actions.query import (
    query_country_results_for_competition,
    query_flight_results_for_competition,
    query_flights_in_competition,
    query_overall_results_for_competition,
    query_positions_by_competitor_in_competition,
    query_result_for_competitor_in_competition,
    query_rfs_penalties_in_competition,
    query_task_results_in_competition,
    query_tasks_in_competition,
)
from wmf_scraper.actions.utilities import try_endpoint
from wmf_scraper.database import get_db
from wmf_scraper.models.query import (
    CompetitionOverallWithPosition,
    CompetitorOverallByTask,
    CompetitorResults,
    CountryResultsWithPosition,
    FlightInCompetition,
    RFSPenaltiesByCompetition,
    TaskInCompetition,
    TaskResultWithPosition,
)

router = APIRouter()


@router.get(
    "/results_competitor_in_competition",
    summary="Load Results for a Competitor in a Competition",
)
@try_endpoint
async def results_competitor_in_competition(
    competition_id: int,
    competitor_name: str,
    flight_number: int | None = None,
    session: Session = Depends(get_db),
) -> list[CompetitorResults]:
    """Every result of a competitor, or only those of one flight."""
    return await query_result_for_competitor_in_competition(
        competition_id=competition_id,
        competitor_name=competitor_name,
        session=session,
        flight_number=flight_number,
    )


@router.get(
    "/overall_results_competition",
    summary="Overall Results for a Competition",
)
@try_endpoint
async def overall_results_competition(
    competition_id: int, session: Session = Depends(get_db)
) -> list[CompetitionOverallWithPosition]:
    return await query_overall_results_for_competition(competition_id=competition_id, session=session)


@router.get(
    "/overall_results_by_country",
    summary="Country classification for a given competition",
)
@try_endpoint
async def overall_results_by_country(
    competition_id: int, session: Session = Depends(get_db)
) -> list[CountryResultsWithPosition]:
    return await query_country_results_for_competition(competition_id=competition_id, session=session)


@router.get(
    "/position_path_in_competition",
    summary="Positions held in total results by task for a competitor",
)
@try_endpoint
async def position_path_in_competition(
    competition_id: int, competitor_name: str, session: Session = Depends(get_db)
) -> CompetitorOverallByTask:
    return await query_positions_by_competitor_in_competition(
        competition_id=competition_id, competitor_name=competitor_name, session=session
    )


@router.get(
    "/tasks_in_competition",
    summary="Tasks of a competition, as they are stored",
)
@try_endpoint
async def tasks_in_competition(competition_id: int, session: Session = Depends(get_db)) -> list[TaskInCompetition]:
    return await query_tasks_in_competition(competition_id=competition_id, session=session)


@router.get(
    "/task_results_competition",
    summary="Classification of a single task",
)
@try_endpoint
async def task_results_competition(
    competition_id: int, task_order: int, session: Session = Depends(get_db)
) -> list[TaskResultWithPosition]:
    return await query_task_results_in_competition(
        competition_id=competition_id, task_order=task_order, session=session
    )


@router.get(
    "/flights_in_competition",
    summary="Flights of a competition, with their date and their tasks",
)
@try_endpoint
async def flights_in_competition(competition_id: int, session: Session = Depends(get_db)) -> list[FlightInCompetition]:
    return await query_flights_in_competition(competition_id=competition_id, session=session)


@router.get(
    "/flight_results_competition",
    summary="Classification of a single flight",
)
@try_endpoint
async def flight_results_competition(
    competition_id: int, flight_number: int, session: Session = Depends(get_db)
) -> list[CompetitionOverallWithPosition]:
    return await query_flight_results_for_competition(
        competition_id=competition_id, flight_number=flight_number, session=session
    )


@router.get(
    "/rfs_penalties",
    summary="RFS penalties for a given competition",
)
@try_endpoint
async def rfs_penalties(competition_id: int, session: Session = Depends(get_db)) -> list[RFSPenaltiesByCompetition]:
    return await query_rfs_penalties_in_competition(competition_id=competition_id, session=session)
