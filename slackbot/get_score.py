import logging
import os
import re
from typing import Dict
from urllib import parse

import psycopg2
from werkzeug.datastructures import ImmutableMultiDict

from database.user import check_score
from slackbot.exceptions import GetScoreError, UserNotFound

logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')

check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")


def get_score(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Get score request: {form}")
    text = form.get('text', '')
    try:
        subject_id = parse_get_score(text)
    except GetScoreError:
        return 'some kind of failure message'  # TODO
    team_id = form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        try:
            score = check_score(conn, team_id, subject_id)
        except UserNotFound:
            return "User not found"
        response = {
            "response_type": "in_channel",  # TODO
            "text": f"Score: {score}"
        }

        logger.debug(f"Response: {response}")
        return response


def parse_get_score(text: str) -> str:
    if not check_score_re.match(text):
        raise GetScoreError(text)
    user_id, display_name = text[1:-1].split('|')
    return user_id
