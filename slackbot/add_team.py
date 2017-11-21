import logging

from werkzeug.datastructures import ImmutableMultiDict

from database.main import connect
from database.team import setup_team

logger = logging.getLogger(__name__)


def add_team(form: ImmutableMultiDict):
    logger.debug(f"Add team request: {form}")
    # TODO: get team id
    team_id = ''
    with connect() as conn:
        setup_team(conn, team_id)
