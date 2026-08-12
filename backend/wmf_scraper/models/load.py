from sqlmodel import SQLModel

from wmf_scraper.models.competition import CompetitionModel


class LoadCompetitionRequest(SQLModel):
    competition_id: int


class LoadIncorrectTaskResponse(SQLModel):
    competitor_no_result: list[str] | None = None
    result_no_competitor: list[str] | None = None
    task_order: int


class LoadCompetitionResponse(SQLModel):
    competition_loaded: CompetitionModel
    incorrect_tasks_loaded: list[LoadIncorrectTaskResponse] = []
    data_changed: bool = False
    status: str = "OK"

    def add_incorrect_task(self, task: LoadIncorrectTaskResponse) -> None:
        self.incorrect_tasks_loaded.append(task)
        self.status = "ERROR!!!"
