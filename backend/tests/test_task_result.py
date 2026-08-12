import pytest
from pytest_mock import MockerFixture

from tests.conftest import (
    get_expected_task_results,
    get_test_files,
    get_xml_tree_from_file,
)
from wmf_scraper.models.task import TaskModel
from wmf_scraper.parsers.task_results import (
    ParsedTask,
    TaskResultRow,
    competitors_from_parsed_tasks,
    parse_task_page,
    resolve_task_results,
)

TESTS_TO_RUN: str = "**/*.html"
DATA_TESTS_FOLDER: str = "data/task_results"
DUMMY_TASK_MODEL = TaskModel(
    task_url="dummy",
    task_name="dummy",
    task_status="dummy",
    task_order=-1,
    competition_id=-1,
)

HTML_FILES = get_test_files(DATA_TESTS_FOLDER, TESTS_TO_RUN)


def a_row(name: str, country: str = "Spain") -> TaskResultRow:
    return TaskResultRow(
        competitor_name=name,
        competitor_country=country,
        tr_result="1.23",
        tr_gross_score=1000,
        tr_task_penalty=0,
        tr_competition_penalty=0,
        tr_net_score=1000,
        tr_notes="",
    )


@pytest.mark.parametrize("html_file", HTML_FILES)
def test_task_results_parser(html_file, mocker: MockerFixture):
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    parsed = parse_task_page(DUMMY_TASK_MODEL)
    expected = get_expected_task_results(html_file)
    assert len(parsed.rows) == expected.expected_number_task_results


@pytest.mark.parametrize("html_file", HTML_FILES)
def test_parsed_rows_carry_name_and_country(html_file, mocker: MockerFixture):
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    parsed = parse_task_page(DUMMY_TASK_MODEL)
    assert all(row.competitor_name for row in parsed.rows)
    assert all(row.competitor_country for row in parsed.rows)


@pytest.mark.parametrize("html_file", HTML_FILES)
def test_roster_can_be_rebuilt_from_task_results(html_file, mocker: MockerFixture):
    """A competition with no published competitor list still yields a roster."""
    mocker.patch(
        "wmf_scraper.parsers.utilities._html_from_url",
        return_value=get_xml_tree_from_file(html_file),
    )
    parsed = parse_task_page(DUMMY_TASK_MODEL)
    competitors = competitors_from_parsed_tasks([parsed])
    assert competitors
    assert len(competitors) == len({row.competitor_name for row in parsed.rows})
    assert all(c.competitor_name and c.competitor_country for c in competitors)


def test_roster_from_tasks_deduplicates_across_tasks():
    tasks = [
        ParsedTask(task_id=1, rows=[a_row("ZEBERLI, Stefan"), a_row("BAREFORD, Dominic")]),
        ParsedTask(task_id=2, rows=[a_row("ZEBERLI, Stefan"), a_row("AYALA, Ivan")]),
    ]
    names = [c.competitor_name for c in competitors_from_parsed_tasks(tasks)]
    assert names == ["ZEBERLI, Stefan", "BAREFORD, Dominic", "AYALA, Ivan"]


def test_unresolved_competitors_are_skipped_not_stored():
    """The whole point: unknown names must never share a placeholder id.

    (task_id, competitor_id) is the primary key, so two unresolved rows in one
    task used to collide with a UNIQUE constraint error.
    """
    tasks = [ParsedTask(task_id=7, rows=[a_row("KNOWN, Pilot"), a_row("GHOST, One"), a_row("GHOST, Two")])]
    results, unmatched = resolve_task_results(tasks, {"KNOWN, Pilot": 42})

    assert [(r.task_id, r.competitor_id) for r in results] == [(7, 42)]
    assert unmatched == {7: ["GHOST, One", "GHOST, Two"]}


def test_every_competitor_resolves_when_the_roster_is_complete():
    tasks = [ParsedTask(task_id=7, rows=[a_row("A, One"), a_row("B, Two")])]
    results, unmatched = resolve_task_results(tasks, {"A, One": 1, "B, Two": 2})

    assert len(results) == 2
    assert unmatched == {}
