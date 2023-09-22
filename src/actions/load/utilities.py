from typing import List

from models.load import LoadTaskResponse
from models.task import TaskModel
from models.task_result import TaskResultModel


def get_load_results_response(
    results_for_task: List[TaskResultModel],
    competitor_names: List[str],
    task_info: TaskModel,
) -> LoadTaskResponse:
    competitors = set(competitor_names)
    competitors_with_results = set([x.competitor_name for x in results_for_task])
    result = LoadTaskResponse(
        task_order=task_info.task_order,
        load_message="OK",
    )
    if competitors_with_results - competitors:
        result.load_message = "ERROR!!"
        result.result_no_competitor = list(competitors_with_results - competitors)
    if competitors - competitors_with_results:
        result.load_message = "ERROR!!"
        result.competitor_no_result = list(competitors - competitors_with_results)
    return result
