from typing import List

from sqlmodel import SQLModel

from models.competition import CompetitionModel
from models.task import TaskModel
from models.task_result import TaskResultModel


class LoadCompetitionRequest(SQLModel):
    competition_id: int


class LoadCompetitionTaskResultsResponse(SQLModel):
    task_loaded: TaskModel
    task_results_loaded: List[TaskResultModel]


class LoadCompetitionResponse(SQLModel):
    competition_loaded: CompetitionModel
    tasks_loaded: List[LoadCompetitionTaskResultsResponse]
