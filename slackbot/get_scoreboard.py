import logging
import os
import psycopg2
from urllib import parse
from werkzeug.datastructures import ImmutableMultiDict
from typing import Dict

logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


def get_scoreboard(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Scoreboard request: {form}")
    team_id = form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        scoreboard = check_all_scores(conn, team_id)
        response = {
            "response_type": "in_channel",  # TODO
            "text": scoreboard
        }

        logger.debug(f"Response: {response}")
        return response