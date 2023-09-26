# from parser.competitor import get_competitor_data
# from typing import List

# from sqlmodel import Session, select

# from actions.utils import exists_record
# from models.competition import CompetitionModel
# from models.competitor import CompetitorModel, CompetitorSimpleModel


# async def load_competitors_for_competition(
#     competition: CompetitionModel, session: Session
# ) -> List[str]:
#     async def add_competitor_if_new(
#         competitors_to_add: List[CompetitorSimpleModel],
#     ) -> List[str]:
#         result = []
#         for competitor in competitors_to_add:
#             query = select(CompetitorModel).where(
#                 CompetitorModel.name == competitor.name
#             )
#             if not exists_record(query, session=session):
#                 session.add(CompetitorModel(**competitor.dict()))
#             result.append(competitor.name)
#         return result

#     return await add_competitor_if_new(get_competitor_data(competition))
