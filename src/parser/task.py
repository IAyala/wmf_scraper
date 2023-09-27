import re
from parser.utilities import URL_PREFIX, html_from_url
from typing import List, Tuple

from actions.utilities import optional_to_int_fallback_0
from models.competition import CompetitionModel
from models.task import TaskModel


def task_order_and_name_from_string(the_data: str) -> Tuple[int, str]:
    """Get the Task data from the title"""
    result = re.search(r"Task (\d*) - (.*)", the_data)
    if result:
        return int(result.group(1)), result.group(2)
    raise ValueError(f"Not possible to extract Task ID and name from: {the_data}")


def first_text(elements: List) -> str:
    return elements[0].text


def get_tasks_data(the_competition: CompetitionModel) -> List[TaskModel]:
    is_last: bool = False
    result = []
    page = html_from_url(the_competition.competition_url)
    for task_info in page.findall(".//a[@class='text-black']"):
        if task_info.getnext() is not None and task_info.getnext().tag == "h5":
            is_last = True
        task_url = task_info.get("href")
        data_to_process = first_text(task_info.findall(".//h7[@class='mb-0']"))
        task_order, task_name = task_order_and_name_from_string(data_to_process)
        task_status = first_text(task_info.findall(r".//div[@class='ms-auto']/h7"))
        result.append(
            TaskModel(
                task_url=f"{URL_PREFIX}/{task_url}",
                task_name=task_name,
                task_status=task_status,
                task_order=task_order,
                competition_id=optional_to_int_fallback_0(
                    the_competition.competition_id
                ),
            )
        )
        if is_last:
            return result
    return result
