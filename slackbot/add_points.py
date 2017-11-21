import logging
import re
from typing import Tuple, Dict

from werkzeug.datastructures import ImmutableMultiDict

from database.user import check_score, update_score
from database.main import connect
from slackbot.exceptions import AddPointsError, UserNotFound

logger = logging.getLogger(__name__)

MAX_SCORE_ADD = 20

add_points_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> [0-9]+( .*)?$")


def add_points(form: ImmutableMultiDict) -> Dict[str, str]:
    logger.debug(f"Add points request: {form}")
    text = form.get('text', '')
    try:
        subject_id, points, reason = parse_add_points(text)
    except AddPointsError:
        return {'text': "Sorry, I don't understand that!"}
    pointer = form.get('')  # TODO
    if pointer and subject_id == pointer:
        return {'text': "Cheeky, you can't give yourself points!"}
    if abs(points) > MAX_SCORE_ADD:
        return {'text': f"Your team only allows adding {MAX_SCORE_ADD} points at once"}
    team_id = form.get('team_id', '')
    with connect() as conn:
        try:
            current_score = check_score(conn, team_id, subject_id)
        except UserNotFound:
            return {'text': "User not found"}
        new_score = current_score + points
        update_score(conn, team_id, subject_id, new_score)
        response = {
            "response_type": "in_channel",  # TODO
            "text": f"<@{subject_id}> is on {new_score} points."
        }

        logger.debug(f"Response: {response}")
        return response


def parse_add_points(text: str) -> Tuple[str, int, str]:
    if not add_points_re.match(text):
        raise AddPointsError(text)
    ltatidentity = text.split('>')[0]
    pointreason = '>'.join(text.split('>')[1:])
    points = int(pointreason[1:].split(' ')[0])
    reason = ' '.join(pointreason[1:].split(' ')[1:])
    identity = ltatidentity[2:]
    user_id, display_name = identity.split('|')  # TODO do something with display name?
    return user_id, points, reason
