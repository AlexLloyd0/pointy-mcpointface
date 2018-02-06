import logging

from werkzeug.datastructures import ImmutableMultiDict

from pointy.database.common import connect
from pointy.database.team import setup_team

logger = logging.getLogger(__name__)


def add_team(form: ImmutableMultiDict):
    logger.debug(f"Add team request: {form}")
    # TODO: get team id
    team_id = form['team_id']
    with connect() as conn:
        setup_team(conn, team_id)
