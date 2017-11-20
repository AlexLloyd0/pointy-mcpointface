import logging
import os
import psycopg2
import re

from urllib import parse
from werkzeug.datastructures import ImmutableMultiDict
from typing import Tuple, Dict

from slackbot.database import check_score, check_all_scores, update_database, setup_team
from slackbot.exceptions import AddPointsError, GetScoreError, UserNotFound

logger = logging.getLogger(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')

MAX_SCORE_ADD = 20

add_points_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> [0-9]+( .*)?$")


def add_points(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Add points request: {form}")
    text = form.get('text', '')
    try:
        subject_id, points, reason = parse_add_points(text)
    except AddPointsError:
        return "Sorry, I don't understand that!"
    pointer = form.get('')  # TODO
    if pointer and subject_id == pointer.lower():
        return "Cheeky, you can't give yourself points!"
    if abs(points) > MAX_SCORE_ADD:
        return f"Your team only allows adding {MAX_SCORE_ADD} points at once"
    team_id = form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        try:
            current_score = check_score(conn, team_id, subject_id)
        except UserNotFound:
            return "User not found"
        new_score = current_score + points
        update_database(conn, team_id, subject_id, new_score)
        response = {
            "response_type": "in_channel",  # TODO
            "text": "test"
        }

        logger.debug(f"Response: {response}")
        return response


def parse_add_points(text: str) -> Tuple[str, int, str]:
    if not add_points_re.match(text):
        raise AddPointsError(text)
    ltidentity = text.split('>')[0]
    pointreason = '>'.join(text.split('>')[1:])
    points = int(pointreason[1:].split(' ')[0])
    reason = ' '.join(pointreason[1:].split(' ')[1:])
    identity = ltidentity[1:]
    user_id, display_name = identity.split('|')  # TODO do something with display name?
    return user_id, points, reason
