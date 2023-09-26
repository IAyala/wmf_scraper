# from parser.task import get_tasks_data
# from typing import List

# from sqlmodel import Session, select

# from models.competition import CompetitionModel
# from models.task import TaskModel


# async def load_tasks_for_competition(
#     competition: CompetitionModel, session: Session
# ) -> List[TaskModel]:
#     async def remove_previous_tasks():
#         prev_tasks = session.exec(
#             select(TaskModel).where(
#                 TaskModel.competition_id == competition.competition_id
#             )
#         )
#         for task in prev_tasks:
#             session.delete(task)

#     async def add_new_tasks(tasks_to_add: List[TaskModel]) -> List[TaskModel]:
#         for updated_task in tasks_to_add:
#             session.add(updated_task)
#         return session.exec(
#             select(TaskModel).where(
#                 TaskModel.competition_id == competition.competition_id
#             )
#         ).all()

#     await remove_previous_tasks()
#     return await add_new_tasks(get_tasks_data(competition))
