import multiprocessing
from functools import partial
from itertools import chain
from parser.parse_utilities import html_from_url
from parser.task import get_tasks_data
from typing import List, Optional, Union

from lxml.html import HtmlElement

from common.utilities import timeit
from models.competition import CompetitionModel
from models.task import TaskModel
from models.task_result import TaskResultModel


def try_int_fallback_zero(value: Union[int, str]) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def get_task_results(
    competition_id: Optional[int], task_data: TaskModel
) -> List[TaskResultModel]:
    if not competition_id:
        raise ValueError(
            "Competition_id must be initialized in method `get_task_results`"
        )
    result = []
    page = html_from_url(task_data.url)
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
                    competition_id=competition_id,
                    competitor_name=competitor_name,
                    task_result_id=task_data.task_id,
                    result=result_content[0],
                    gross_score=result_content[1],
                    task_penalty=try_int_fallback_zero(result_content[2]),
                    competition_penalty=try_int_fallback_zero(result_content[3]),
                    net_score=result_content[4],
                    notes=result_content[5],
                )
            )
    return result


@timeit
def get_tasks_results_data(the_competition: CompetitionModel) -> List[TaskResultModel]:
    result = []
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    result = pool.map(
        partial(get_task_results, the_competition.competition_id),
        get_tasks_data(the_competition),
    )
    pool.close()
    pool.join()
    return list(chain.from_iterable(result))
