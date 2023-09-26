from parser.parse_utilities import html_from_url
from typing import List

from models.competition import CompetitionModel
from models.competitor import CompetitorModel


def get_competitor_data(
    the_competition: CompetitionModel,
) -> List[CompetitorModel]:
    result = []
    page = html_from_url(the_competition.competition_url)
    for competitors_info in page.findall(".//tbody"):
        competitors = competitors_info.findall(".//tr")
        for competitor in competitors:
            info = [td.text_content() for td in competitor.findall(".//td")]
            competitor_name = info[1].split(" - ")[1]
            competitor_country = info[2]
            result.append(
                CompetitorModel(
                    competitor_name=competitor_name,
                    competitor_country=competitor_country,
                )
            )
    return result
