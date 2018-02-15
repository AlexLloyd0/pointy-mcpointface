import logging
from typing import Mapping

from pointy.database.common import connect
from pointy.database.team import setup_team

logger = logging.getLogger(__name__)


def add_team(form: Mapping, test: bool = False):
    logger.debug(f"Add team request: {form}")
    # TODO: get team id
    team_id = form['team_id']
    with connect(test) as conn:
        setup_team(conn, team_id)
