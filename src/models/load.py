# from typing import List, Optional

# from sqlmodel import SQLModel

# from models.competition import CompetitionModel


# class LoadCompetitionRequest(SQLModel):
#     competition_id: int


# class LoadTaskResponse(SQLModel):
#     competitor_no_result: Optional[List[str]] = None
#     result_no_competitor: Optional[List[str]] = None
#     load_message: str
#     task_order: int


# class LoadCompetitionResponse(SQLModel):
#     status: str = "OK"
#     competition_loaded: CompetitionModel
#     tasks_loaded: List[LoadTaskResponse] = []
