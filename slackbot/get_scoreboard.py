import logging
from typing import Dict, List, Tuple

from werkzeug.datastructures import ImmutableMultiDict

from database.main import connect, channel_resp
from database.team import check_all_scores

logger = logging.getLogger(__name__)


def get_scoreboard(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Scoreboard request: {form}")
    team_id = form.get('team_id', '')
    with connect() as conn:
        scoreboard_list = check_all_scores(conn, team_id)
    return channel_resp(_parse_scoreboard(scoreboard_list))


def _parse_scoreboard(scoreboard_list: List[Tuple[str, int]]) -> str:
    text = f'Here\'s a list of my favourite people:'
    for index, (subject, score) in enumerate(scoreboard_list):
        text += f'\n{index+1}. {subject} [{score} point{"s" if score != 1 else ""}]'
        if index == 0:
            text += ' :crown:'
        elif index + 1 == len(scoreboard_list):
            text += ' :hankey:'
    return text
