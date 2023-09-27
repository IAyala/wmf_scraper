import multiprocessing
from functools import partial
from itertools import chain
from parser.competitor import get_competitor_data
from parser.task import get_tasks_data
from parser.utilities import html_from_url
from typing import List, Optional, Union

from lxml.html import HtmlElement
from sqlmodel import Session

from actions.competitor import competitors_mapping
from models.competition import CompetitionModel
from models.task import TaskModel
from models.task_result import TaskResultModel


def try_int_fallback_zero(value: Union[int, str]) -> int:
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def get_competition_id_from_name(
    competitor_name: str, competitors_mapping: Optional[dict]
) -> int:
    if competitors_mapping and competitor_name in competitors_mapping:
        return competitors_mapping[competitor_name]
    return -1


def get_task_results(
    task_data: TaskModel, competitors_mapping: Optional[dict] = None
) -> List[TaskResultModel]:
    result: List[TaskResultModel] = []
    page = html_from_url(task_data.task_url)
    for task_results_info in page.findall(".//tbody"):
        task_results: List[HtmlElement] = task_results_info.findall(".//tr")
        for task_result in task_results:
            competitor_name = (
                task_result.findall(".//span[@class='fw-semibold']")[0]
                .text_content()
                .split(" - ")[1]
            )
            result_content = [td.text_content() for td in task_result.findall(".//td")][
                2:
            ]
            result.append(
                TaskResultModel(
                    task_id=task_data.task_id,
                    competitor_id=get_competition_id_from_name(
                        competitor_name, competitors_mapping
                    ),
                    tr_result=result_content[0],
                    tr_gross_score=try_int_fallback_zero(result_content[1]),
                    tr_task_penalty=try_int_fallback_zero(result_content[2]),
                    tr_competition_penalty=try_int_fallback_zero(result_content[3]),
                    tr_net_score=try_int_fallback_zero(result_content[4]),
                    tr_notes=result_content[5],
                )
            )
    return result


def get_task_results_parallel(
    tasks: List[TaskModel], competitors: dict
) -> List[TaskResultModel]:
    result = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    result = pool.map(
        partial(get_task_results, competitors_mapping=competitors),
        tasks,
    )
    pool.close()
    pool.join()
    return list(chain.from_iterable(result))


def get_tasks_results_data(
    the_competition: CompetitionModel, session: Session
) -> List[TaskResultModel]:
    competitors_in_competition = get_competitor_data(the_competition)
    the_competitors = competitors_mapping(competitors_in_competition, session=session)
    return get_task_results_parallel(get_tasks_data(the_competition), the_competitors)
