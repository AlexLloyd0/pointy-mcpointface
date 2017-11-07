from typing import Tuple
import re

from slackbot.exceptions import AddPointsError, GetScoreError


check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")
add_points_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> [0-9]+( .*)?$")


def parse_add_points(text: str) -> Tuple[str, int, str]:
    if not add_points_re.match(text):
        raise AddPointsError(text)
    ltidentity = text.split('>')[0]
    pointreason = '>'.join(text.split('>')[1:])
    points = int(pointreason[1:].split(' ')[0])
    reason = ' '.join(pointreason[1:].split(' ')[1:])
    identity = ltidentity[1:]
    user_id, display_name = identity.split('|')  # TODO ????
    user_id = user_id.lower()
    return user_id, points, reason


def parse_get_score(text: str) -> str:
    if not check_score_re.match(text):
        raise GetScoreError(text)
    user_id, display_name = text[1:-1].split('|')
    return user_id
