import logging
import os
import psycopg2

from urllib import parse
from werkzeug.datastructures import ImmutableMultiDict
from typing import Dict

from database.team import check_all_scores
from database.main import connect

logger = logging.getLogger(__name__)


def get_scoreboard(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Scoreboard request: {form}")
    team_id = form.get('team_id', '')
    with connect() as conn:
        scoreboard = check_all_scores(conn, team_id)
        response = {
            "response_type": "in_channel",  # TODO
            "text": scoreboard
        }

        logger.debug(f"Response: {response}")
        return response
