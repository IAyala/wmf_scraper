"""Parsing of WatchMeFly task result pages.

A task page is parsed once into plain rows that still carry the competitor's
name. Competitor ids are resolved afterwards, so the roster can come either
from the competition's standings table or, when that has not been published
yet, from the task results themselves.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import NamedTuple

from loguru import logger
from lxml.html import HtmlElement
from sqlmodel import Session

from wmf_scraper.actions.competitor import competitors_mapping
from wmf_scraper.models.competition import CompetitionModel
from wmf_scraper.models.competitor import CompetitorModel
from wmf_scraper.models.task import TaskModel
from wmf_scraper.models.task_result import TaskResultModel
from wmf_scraper.parsers.competitor import get_competitor_data
from wmf_scraper.parsers.task import get_tasks_data
from wmf_scraper.parsers.utilities import html_from_url

# Enough to overlap the per-page HTTP latency without hammering WatchMeFly.
MAX_PARSE_WORKERS = 8


class TaskResultRow(NamedTuple):
    """One result line, before the competitor has been resolved to an id."""

    competitor_name: str
    competitor_country: str
    tr_result: str
    tr_gross_score: int
    tr_task_penalty: int
    tr_competition_penalty: int
    tr_net_score: int
    tr_notes: str


class ParsedTask(NamedTuple):
    task_id: int | None
    rows: list[TaskResultRow]


def try_int_fallback_zero(value: int | str) -> int:
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def _competitor_name(row: HtmlElement) -> str:
    return row.findall(".//span[@class='fw-semibold']")[0].text_content().split(" - ")[1].strip()


def _competitor_country(row: HtmlElement) -> str:
    countries = row.findall(".//span[@class='fs-sm text-muted']")
    return countries[0].text_content().strip() if countries else ""


def _row_from_html(row: HtmlElement) -> TaskResultRow:
    # The first two cells are the rank and the competitor; the rest is the score.
    score = [td.text_content() for td in row.findall(".//td")][2:]
    return TaskResultRow(
        competitor_name=_competitor_name(row),
        competitor_country=_competitor_country(row),
        tr_result=score[0],
        tr_gross_score=try_int_fallback_zero(score[1]),
        tr_task_penalty=try_int_fallback_zero(score[2]),
        tr_competition_penalty=try_int_fallback_zero(score[3]),
        tr_net_score=try_int_fallback_zero(score[4]),
        tr_notes=score[5],
    )


def parse_task_page(task_data: TaskModel) -> ParsedTask:
    page = html_from_url(task_data.task_url)
    rows = [_row_from_html(row) for results_info in page.findall(".//tbody") for row in results_info.findall(".//tr")]
    return ParsedTask(task_id=task_data.task_id, rows=rows)


def parse_tasks_parallel(tasks: list[TaskModel]) -> list[ParsedTask]:
    """Fetch and parse every task page concurrently, preserving task order.

    Threads rather than processes: the work is dominated by HTTP latency, and
    both urllib and lxml release the GIL. It also avoids forking a pool out of
    the async server process, which is fragile and, since Python 3.14 defaults
    to the forkserver start method, needs an importable __main__.
    """
    if not tasks:
        return []
    with ThreadPoolExecutor(max_workers=min(MAX_PARSE_WORKERS, len(tasks))) as pool:
        return list(pool.map(parse_task_page, tasks))


def competitors_from_parsed_tasks(parsed_tasks: list[ParsedTask]) -> list[CompetitorModel]:
    """Build the roster from the task results, in first-seen order.

    Used when the competition's standings table has no competitors yet, which
    is how WatchMeFly presents an event whose tasks are all still provisional.
    """
    seen: dict[str, str] = {}
    for parsed_task in parsed_tasks:
        for row in parsed_task.rows:
            seen.setdefault(row.competitor_name, row.competitor_country)
    return [CompetitorModel(competitor_name=name, competitor_country=country) for name, country in seen.items()]


def resolve_task_results(
    parsed_tasks: list[ParsedTask], competitors: dict
) -> tuple[list[TaskResultModel], dict[int, list[str]]]:
    """Turn parsed rows into database rows, dropping competitors we cannot resolve.

    Returns the results together with, per task id, the competitor names that
    had a result but no matching competitor. Those rows are skipped rather than
    stored: (task_id, competitor_id) is the primary key, so writing them under a
    placeholder id both corrupts the task and collides as soon as there is more
    than one of them.
    """
    results: list[TaskResultModel] = []
    unmatched: dict[int, list[str]] = {}
    for parsed_task in parsed_tasks:
        for row in parsed_task.rows:
            competitor_id = competitors.get(row.competitor_name)
            if competitor_id is None:
                unmatched.setdefault(parsed_task.task_id or 0, []).append(row.competitor_name)
                logger.warning(
                    f"Task {parsed_task.task_id}: no competitor matches '{row.competitor_name}', result skipped"
                )
                continue
            results.append(
                TaskResultModel(
                    task_id=parsed_task.task_id,
                    competitor_id=competitor_id,
                    tr_result=row.tr_result,
                    tr_gross_score=row.tr_gross_score,
                    tr_task_penalty=row.tr_task_penalty,
                    tr_competition_penalty=row.tr_competition_penalty,
                    tr_net_score=row.tr_net_score,
                    tr_notes=row.tr_notes,
                )
            )
    return results, unmatched


def competitors_for_competition(competition: CompetitionModel, parsed_tasks: list[ParsedTask]) -> list[CompetitorModel]:
    """The competition's roster, falling back to the task results when needed."""
    competitors = get_competitor_data(competition)
    if competitors:
        return competitors
    competitors = competitors_from_parsed_tasks(parsed_tasks)
    logger.warning(
        f"Competition {competition.competition_id} publishes no competitor list yet; "
        f"took {len(competitors)} competitors from the task results instead"
    )
    return competitors


def get_tasks_results_data(the_competition: CompetitionModel, session: Session) -> list[TaskResultModel]:
    parsed_tasks = parse_tasks_parallel(get_tasks_data(the_competition))
    competitors = competitors_for_competition(the_competition, parsed_tasks)
    results, _ = resolve_task_results(parsed_tasks, competitors_mapping(competitors, session=session))
    return results
