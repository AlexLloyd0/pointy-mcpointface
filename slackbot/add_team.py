import logging
import os
from urllib import parse

import psycopg2
from werkzeug.datastructures import ImmutableMultiDict

from database.team import setup_team

logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


def add_team(form: ImmutableMultiDict):
    logger.debug(f"Add team request: {form}")
    # TODO: get team id
    team_id = ''
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        setup_team(conn, team_id)
