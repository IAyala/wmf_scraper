from parser.parse_utilities import html_from_url
from typing import List

from models.competition import CompetitionModel
from models.competitor import CompetitorModel


def get_competitor_data(the_competition: CompetitionModel) -> List[CompetitorModel]:
    result = []
    page = html_from_url(the_competition.url)
    for competitors_info in page.findall(".//tbody"):
        competitors = competitors_info.findall(".//tr")
        for competitor in competitors:
            info = [td.text_content() for td in competitor.findall(".//td")]
            competitor_banner, competitor_name = info[1].split(" - ")
            competitor_country = info[2]
            result.append(
                CompetitorModel(
                    name=competitor_name,
                    country=competitor_country,
                    banner_number=competitor_banner,
                    competition_id=the_competition.competition_id,
                )
            )
    return result
