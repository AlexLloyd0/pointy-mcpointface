import logging
from typing import Dict

from werkzeug.datastructures import ImmutableMultiDict

from database.main import connect, channel_resp
from database.team import check_all_scores

logger = logging.getLogger(__name__)


def get_scoreboard(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Scoreboard request: {form}")
    team_id = form.get('team_id', '')
    with connect() as conn:
        scoreboard = check_all_scores(conn, team_id)
        return channel_resp(str(scoreboard))
