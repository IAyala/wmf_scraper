import re
from typing import List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from lxml import html

from models.competition import CompetitionModel
from models.task import TaskModel


def html_from_url(url: str):  # pragma: no cover
    try:
        with urlopen(url) as the_url_reader:
            return html.fromstring(the_url_reader.read())
    except (HTTPError, URLError) as ex:
        raise ValueError(f"Not possible to open URL: {url}") from ex


def task_id_and_name_from_string(the_data: str) -> Tuple[int, str]:
    """Get the Task data from the title"""
    result = re.search(r"Task (\d*) - (.*)", the_data)
    if result:
        return int(result.group(1)), result.group(2)
    raise ValueError(f"Not possible to extract Task ID and name from: {the_data}")


def first_text(elements: List) -> str:
    return elements[0].text


def get_tasks_data(the_competition: CompetitionModel) -> List[TaskModel]:
    result = []
    page = html_from_url(the_competition.url)
    for task_info in page.findall(".//a[@class='text-black']"):
        task_url = task_info.get("href")
        data_to_process = first_text(task_info.findall(".//h7[@class='mb-0']"))
        task_id, task_name = task_id_and_name_from_string(data_to_process)
        task_status = first_text(task_info.findall(r".//div[@class='ms-auto']/h7"))
        result.append(
            TaskModel(
                url=task_url,
                name=task_name,
                status=task_status,
                task_id=task_id,
                competition_id=the_competition.competition_id,
            )
        )
    return result
