import logging
import os
from urllib import parse

import psycopg2
from flask import Flask, request

from slackbot.add_points import add_points
from slackbot.database import check_score, check_all_scores, update_database, setup_team
from slackbot.exceptions import AddPointsError, GetScoreError, UserNotFound

logger = logging.getLogger(__name__)

app = Flask(__name__)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])
verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


MAX_SCORE_ADD = 20


@app.route('/add-points', methods=['POST'])
def add_points_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':
        return  # TODO
    add_points(form)



@app.route('/get-score', methods=['POST'])
def get_score_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
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


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
    logger.debug(f"Scoreboard request: {form}")
    team_id = form.get('team_id', '')
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
def add_team_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
    logger.debug(f"Add team request: {form}")
    # TODO: get team id
    team_id = ''
    with psycopg2.connect(database=url.path[1:],
                          user=url.username,
                          password=url.password,
                          host=url.hostname,
                          port=url.port) as conn:
        setup_team(conn, team_id)


def main():
    app.run(host='0.0.0.0')
