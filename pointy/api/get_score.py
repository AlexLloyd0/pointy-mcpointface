import logging
import re
from typing import Dict

from werkzeug.datastructures import ImmutableMultiDict

from pointy.database.common import connect, ephemeral_resp, channel_resp
from pointy.database.user import check_score
from pointy.exceptions import GetScoreError, UserNotFound

logger = logging.getLogger(__name__)

check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")


def get_score(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Get score request: {form}")
    text = form.get('text', '')
    try:
        subject_id = parse_get_score(text)
    except GetScoreError:
        return ephemeral_resp(f"Could not parse {text}")
    team_id = form.get('team_id', '')
    with connect() as conn:
        try:
            score = check_score(conn, team_id, subject_id)
        except UserNotFound:
            return ephemeral_resp(f"User not found")  # TODO add them if they're a user?
        return channel_resp(f"{text.strip()} has {score} point{'s' if score != 1 else ''}")


def parse_get_score(text: str) -> str:
    if not check_score_re.match(text):
        raise GetScoreError(text)
    user_id, display_name = text.strip()[2:-1].split('|')
    return user_id
