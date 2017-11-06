import logging
import os
import re
from typing import Tuple
from urllib import parse

import psycopg2
from flask import Flask, request

from slackbot.database import check_score, check_all_scores, update_database, setup_team

logger = logging.getLogger(__name__)

app = Flask(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
api_token = os.environ.get('POINTY_APP_TOKEN')
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')

add_points_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> [0-9]+( .*)?$")
check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")

MAX_SCORE_ADD = 20


@app.route('/add-points', methods=['POST'])
def add_points():
    if request.form.get('token') != verify_token:
        return
    logger.debug(f"Add points request: {request.form}")
    text = request.form.get('text', '')
    try:
        subject_id, points, reason = parse_add_points(text)
    except AddPointsError:
        return "Sorry, I don't understand that!"
    if subject_id == request.form.get(''):  # TODO
        return "Cheeky, you can't give yourself points!"
    if abs(points) > MAX_SCORE_ADD:
        return f"Your team only allows adding {MAX_SCORE_ADD} points at once"
    team_id = request.form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:

        current_score = check_score(conn, team_id, subject_id)
        new_score = current_score + points
        update_database(conn, team_id, subject_id, new_score)
        response = {
            "response_type": "in_channel",  # TODO
            "text": "test"
        }

        logger.debug(f"Response: {response}")
        return response


@app.route('/get-score', methods=['POST'])
def get_score():
    if request.form.get('token') != verify_token:
        return
    logger.debug(f"Get score request: {request.form}")
    text = request.form.get('text', '')
    try:
        subject_id = parse_get_score(text)
    except GetScoreError:
        return 'some kind of failure message'  # TODO
    team_id = request.form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:

        score = check_score(conn, team_id, subject_id)

        response = {
            "response_type": "in_channel",  # TODO
            "text": f"Score: {score}"
        }

        logger.debug(f"Response: {response}")
        return response


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard():
    if request.form.get('token') != verify_token:
        return
    logger.debug(f"Scoreboard request: {request.form}")
    team_id = request.form.get('team_id', '')
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        scoreboard = check_all_scores(conn, team_id)
        response = {
            "response_type": "in_channel",  # TODO
            "text": scoreboard
        }

        logger.debug(f"Response: {response}")
        return response


@app.route('/add-team', methods=['POST'])
def add_team():
    if request.form.get('token') != verify_token:
        return
    logger.debug(f"Add team request: {request.form}")
    # TODO: get team id
    team_id = ''
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        setup_team(conn, team_id)


class AddPointsError(SyntaxError):
    pass  # TODO


class GetScoreError(SyntaxError):
    pass  # TODO


def parse_add_points(text: str) -> Tuple[str, int, str]:
    if not add_points_re.match(text):
        raise AddPointsError(text)
    ltidentity = text.split('>')[0]
    pointreason = '>'.join(text.split('>')[1:])
    points = int(pointreason[1:].split(' ')[0])
    reason = ' '.join(pointreason[1:].split(' ')[1:])
    identity = ltidentity[1:]
    user_id, display_name = identity.split('|')  # TODO ????
    return user_id, points, reason


def parse_get_score(text: str) -> str:
    if not get_score.match(text):
        raise GetScoreError(text)
    user_id, display_name = text[1:-1].split('|')
    return user_id


def main():
    app.run(host='0.0.0.0')
