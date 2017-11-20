from typing import Tuple
from werkzeug.datastructures import ImmutableMultiDict
import re

from slackbot.exceptions import AddPointsError, GetScoreError


check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")



def parse_get_score(text: str) -> str:
    if not check_score_re.match(text):
        raise GetScoreError(text)
    user_id, display_name = text[1:-1].split('|')
    return user_id
