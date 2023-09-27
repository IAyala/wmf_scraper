from typing import List, Optional

from sqlmodel import SQLModel

from models.competition import CompetitionModel


class LoadCompetitionRequest(SQLModel):
    competition_id: int


class LoadIncorrectTaskResponse(SQLModel):
    competitor_no_result: Optional[List[str]] = None
    result_no_competitor: Optional[List[str]] = None
    task_order: int


class LoadCompetitionResponse(SQLModel):
    competition_loaded: CompetitionModel
    incorrect_tasks_loaded: List[LoadIncorrectTaskResponse] = []
    status: str = "OK"

    def add_incorrect_task(self, task: LoadIncorrectTaskResponse) -> None:
        self.incorrect_tasks_loaded.append(task)
        self.status = "ERROR!!!"
