from sqlmodel import Session, col, func, or_, select

from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.query import (
    CompetitionOverall,
    CompetitionOverallWithPosition,
    CompetitorOverallByTask,
    CompetitorResults,
    CountryResults,
    CountryResultsWithPosition,
    FlightInCompetition,
    RFSPenaltiesByCompetition,
    TaskInCompetition,
    TaskResult,
    TaskResultWithPosition,
)
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel


def query_overalls(competition_id: int):
    return (
        select(
            CompetitorModel.competitor_name,
            CompetitorModel.competitor_country,
            func.sum(TaskResultModel.tr_net_score).label("total_score"),  # type: ignore
            func.sum(TaskResultModel.tr_competition_penalty).label("total_competition_penalty"),  # type: ignore
            func.sum(TaskResultModel.tr_task_penalty).label("total_task_penalty"),  # type: ignore
            func.count(TaskResultModel.task_id).label("number_tasks"),  # type: ignore
        )
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .group_by(CompetitorModel.competitor_name)
    )


def query_average_by_country(competition_id: int, session: Session):
    competitors_in_first_task = (
        select(TaskResultModel.competitor_id)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .where(TaskModel.task_order == 1)
        .subquery()
    )

    competitors_per_country = (
        select(
            CompetitorModel.competitor_country,
            func.count(CompetitorModel.competitor_id).label("number_competitors"),  # type: ignore
        )
        .join(
            competitors_in_first_task,
            competitors_in_first_task.c.competitor_id == CompetitorModel.competitor_id,
        )
        .group_by(CompetitorModel.competitor_country)
        .subquery()
    )

    return (
        select(
            CompetitorModel.competitor_country,
            func.sum(TaskResultModel.tr_net_score).label("total_score"),  # type: ignore
            func.count(TaskResultModel.task_id).label("number_tasks"),  # type: ignore
            competitors_per_country.c.number_competitors,
        )
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .join(
            competitors_per_country,
            competitors_per_country.c.competitor_country == CompetitorModel.competitor_country,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .group_by(CompetitorModel.competitor_country)
    )


def query_overalls_up_to_task(competition_id: int, up_to_task: int):
    return query_overalls(competition_id).where(TaskModel.task_order <= up_to_task)


def query_overalls_in_flight(competition_id: int, flight_number: int):
    """The standings of one flight on its own, rather than cumulative."""
    return query_overalls(competition_id).where(TaskModel.flight_number == flight_number)


async def query_result_for_competitor_in_competition(
    competition_id: int, competitor_name: str, session: Session, flight_number: int | None = None
) -> list[CompetitorResults]:
    query = (
        select(TaskResultModel, TaskModel, CompetitorModel, CompetitionModel)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .where(col(CompetitorModel.competitor_name).contains(competitor_name))
    )
    if flight_number is not None:
        query = query.where(TaskModel.flight_number == flight_number)
    all_results = session.exec(query).all()
    return [
        CompetitorResults(
            result=task_result.tr_result,
            gross_score=task_result.tr_gross_score,
            task_penalty=task_result.tr_task_penalty,
            competition_penalty=task_result.tr_competition_penalty,
            net_score=task_result.tr_net_score,
            notes=task_result.tr_notes,
            competitor_name=competitor.competitor_name,
            competitor_country=competitor.competitor_country,
            competition_name=competition.competition_description,
            task_order=task.task_order,
            task_name=task.task_name,
            task_status=task.task_status,
            flight_number=task.flight_number,
            flight_date=task.flight_date,
            flight_period=task.flight_period,
        )
        for task_result, task, competitor, competition in all_results
    ]


async def query_country_results_for_competition(
    competition_id: int, session: Session
) -> list[CountryResultsWithPosition]:
    result = []
    all_results = session.exec(query_average_by_country(competition_id=competition_id, session=session)).all()
    for elem in all_results:
        result.append(
            CountryResults(
                competitor_country=elem.competitor_country,
                number_competitors=elem.number_competitors,
                average_score=round(elem.total_score / elem.number_tasks, 2),
            )
        )
    return [
        CountryResultsWithPosition(**res.dict(), position=pos + 1)
        for pos, res in enumerate(sorted(result, key=lambda x: x.average_score, reverse=True))
    ]


def ranked_overalls(rows) -> list[CompetitionOverallWithPosition]:
    """Turn summed scores into a classification, highest total first."""
    result = [
        CompetitionOverall(
            total_score=elem.total_score,
            average_score=round(elem.total_score / elem.number_tasks, 2),
            total_competition_penalty=elem.total_competition_penalty,
            total_task_penalty=elem.total_task_penalty,
            competitor_name=elem.competitor_name,
            competitor_country=elem.competitor_country,
        )
        for elem in rows
    ]
    return [
        CompetitionOverallWithPosition(**res.dict(), position=pos + 1)
        for pos, res in enumerate(sorted(result, key=lambda x: x.total_score, reverse=True))
    ]


async def query_overall_results_for_competition(
    competition_id: int, session: Session, up_to_task: int | None = None
) -> list[CompetitionOverallWithPosition]:
    query = query_overalls_up_to_task(competition_id, up_to_task) if up_to_task else query_overalls(competition_id)
    return ranked_overalls(session.exec(query).all())


async def query_flight_results_for_competition(
    competition_id: int, flight_number: int, session: Session
) -> list[CompetitionOverallWithPosition]:
    """The classification of a single flight, scored on its own tasks only."""
    return ranked_overalls(session.exec(query_overalls_in_flight(competition_id, flight_number)).all())


def ranked_task_results(results: list[TaskResult]) -> list[TaskResultWithPosition]:
    """Rank one task, sharing a position between equal scores.

    The overall standings can get away with numbering everyone 1, 2, 3: an
    exact tie on the sum of a dozen tasks is rare. A single task ties all the
    time, because half a field can score zero on it. Numbering those 30, 31, 32
    would invent an order the scorers never gave, so equal scores share the
    better position and the next score skips past them.
    """
    ranked = []
    position = 0
    previous_score = None
    for index, result in enumerate(sorted(results, key=lambda x: x.net_score, reverse=True), start=1):
        if result.net_score != previous_score:
            position = index
            previous_score = result.net_score
        ranked.append(TaskResultWithPosition(**result.dict(), position=position))
    return ranked


async def query_tasks_in_competition(competition_id: int, session: Session) -> list[TaskInCompetition]:
    """The stored tasks of a competition, in the order they were flown.

    Read from the database rather than scraped, so picking a task to look at
    does not depend on WatchMeFly being reachable, and so the list can only
    offer tasks whose results are actually stored.
    """
    tasks = session.exec(
        select(TaskModel).where(TaskModel.competition_id == competition_id).order_by(col(TaskModel.task_order))
    ).all()
    return [
        TaskInCompetition(
            task_order=task.task_order,
            task_name=task.task_name,
            task_status=task.task_status,
            flight_number=task.flight_number,
            flight_date=task.flight_date,
            flight_period=task.flight_period,
        )
        for task in tasks
    ]


async def query_task_results_in_competition(
    competition_id: int, task_order: int, session: Session
) -> list[TaskResultWithPosition]:
    """Everyone's result in one task, best score first."""
    all_results = session.exec(
        select(TaskResultModel, CompetitorModel)
        .join(TaskModel, TaskModel.task_id == TaskResultModel.task_id)
        .join(CompetitorModel, CompetitorModel.competitor_id == TaskResultModel.competitor_id)
        .where(TaskModel.competition_id == competition_id)
        .where(TaskModel.task_order == task_order)
    ).all()
    return ranked_task_results(
        [
            TaskResult(
                competitor_name=competitor.competitor_name,
                competitor_country=competitor.competitor_country,
                result=task_result.tr_result,
                gross_score=task_result.tr_gross_score,
                task_penalty=task_result.tr_task_penalty,
                competition_penalty=task_result.tr_competition_penalty,
                net_score=task_result.tr_net_score,
                notes=task_result.tr_notes,
            )
            for task_result, competitor in all_results
        ]
    )


async def query_flights_in_competition(competition_id: int, session: Session) -> list[FlightInCompetition]:
    """The flights of a competition, in flight order, with their tasks.

    Tasks with no flight are left out rather than lumped into a placeholder
    flight: they come from a competition loaded before flights were scraped, or
    from one WatchMeFly does not publish a flights view for.
    """
    tasks = session.exec(
        select(TaskModel)
        .where(TaskModel.competition_id == competition_id)
        .where(col(TaskModel.flight_number).is_not(None))
        .order_by(col(TaskModel.flight_number), col(TaskModel.task_order))
    ).all()
    flights: dict[int, FlightInCompetition] = {}
    for task in tasks:
        if task.flight_number is None:  # pragma: no cover - excluded by the query above
            continue
        flight = flights.setdefault(
            task.flight_number,
            FlightInCompetition(
                flight_number=task.flight_number,
                flight_date=task.flight_date,
                flight_period=task.flight_period,
                task_orders=[],
            ),
        )
        flight.task_orders.append(task.task_order)
    return list(flights.values())


async def query_rfs_penalties_in_competition(competition_id: int, session: Session) -> list[RFSPenaltiesByCompetition]:
    all_results = session.exec(
        select(TaskModel, TaskResultModel, CompetitionModel, CompetitorModel)
        .join(TaskResultModel, TaskResultModel.task_id == TaskModel.task_id)
        .join(
            CompetitionModel,
            TaskModel.competition_id == CompetitionModel.competition_id,
        )
        .join(
            CompetitorModel,
            CompetitorModel.competitor_id == TaskResultModel.competitor_id,
        )
        .where(CompetitionModel.competition_id == competition_id)
        .where(
            or_(
                col(TaskResultModel.tr_notes).contains("10."),
                # col(TaskResultModel.tr_notes).contains("10.3")
            )
        )
    ).all()
    return [
        RFSPenaltiesByCompetition(
            competitor_name=competitor.competitor_name,
            competitor_country=competitor.competitor_country,
            task_number=task.task_order,
            task_description=task.task_name,
            task_penalty=task_result.tr_task_penalty,
            competition_penalty=task_result.tr_competition_penalty,
            notes=task_result.tr_notes,
        )
        for task, task_result, _, competitor in all_results
    ]


def task_orders_in_competition(competition_id: int, session: Session) -> list[int]:
    """The task numbers actually published for a competition, in order.

    WatchMeFly numbers tasks as they are flown, and a cancelled task leaves a
    hole: the 2026 US Nationals go straight from Task 16 to Task 18. Walking
    1..count(tasks) would therefore stop one task short of the end and report a
    path that disagrees with the final overalls.
    """
    return list(
        session.exec(
            select(TaskModel.task_order)
            .where(TaskModel.competition_id == competition_id)
            .distinct()
            .order_by(col(TaskModel.task_order))
        ).all()
    )


async def query_positions_by_competitor_in_competition(
    competition_id: int, competitor_name: str, session: Session
) -> CompetitorOverallByTask:
    task_orders = task_orders_in_competition(competition_id=competition_id, session=session)
    competitor = session.exec(
        select(CompetitorModel).where(CompetitorModel.competitor_name == competitor_name)
    ).one_or_none()
    if task_orders and competitor:
        result = CompetitorOverallByTask(**competitor.dict(), task_orders=task_orders)
        for task_order in task_orders:
            results_up_to_task = await query_overall_results_for_competition(
                competition_id=competition_id, session=session, up_to_task=task_order
            )
            my_competitor_position = next(filter(lambda x: x.competitor_name == competitor_name, results_up_to_task))
            result.competitor_positions.append(my_competitor_position.position)
        return result
    raise ValueError(
        f"Competition with id {competition_id} does not exist, or competitor {competitor_name} does not exist..."
    )
