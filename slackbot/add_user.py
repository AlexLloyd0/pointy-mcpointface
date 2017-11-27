import logging

from werkzeug.datastructures import ImmutableMultiDict

from database.main import connect
from database.team import setup_team

logger = logging.getLogger(__name__)


def add_user(form: ImmutableMultiDict):
    logger.debug(f"Add team request: {form}")
    team_id = form.get('team_id')
    with connect() as conn:
        setup_team(conn, team_id)
