from flask import Flask, request, Response, jsonify
import re
import logging
import os
import psycopg2
from slackclient import SlackClient

from psycopg2.extensions import AsIs
from typing import Tuple, Dict, Optional, List
from urllib import parse

logger = logging.getLogger(__name__)

app = Flask(__name__)

# @@@TODO@@@ check verification token

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])

add_points_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> [0-9]+( .*)?$")
check_score_re = re.compile("^<@[A-Z][a-zA-Z0-9]+(\|[^>]*)?> ?$")
api_token = os.environ.get('POINTY_APP_TOKEN')

MAX_SCORE_ADD = 20


@app.route('/add-points', methods=['POST'])
def add_points():
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
    ltidentity, pointreason = text.split('>')[0]
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


# Database functions:


def check_score(conn, team_id: str, user_id: str, retry: bool = True) -> int:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """SELECT score FROM points.%s WHERE user_id = %s""",
                (AsIs(team_id), user_id)
            )
            score = cur.fetchone()[0]
        except psycopg2.ProgrammingError:
            setup_team(conn, team_id)
            if retry:
                return check_score(conn, team_id, user_id, False)
            else:
                raise
    conn.commit()
    return score


def check_all_scores(conn, team_id: str, retry: bool = True) -> List[Tuple[str, int]]:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """SELECT * FROM points.%s
                ORDER BY score DESC""",
                (AsIs(team_id),)
            )
            scoreboard = cur.fetchall()
        except psycopg2.ProgrammingError:
            setup_team(conn, team_id)
            if retry:
                return check_all_scores(conn, team_id, False)
            else:
                raise
    conn.commit()
    return scoreboard


def update_database(conn, team_id: str, user_id: str, new_score: int, retry: bool = True) -> bool:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """UPDATE points.%s
                SET score = %s
                WHERE user_id = %s""",
                (AsIs(team_id), new_score, user_id)
            )
        except psycopg2.ProgrammingError:
            setup_team(conn, team_id)
            if retry:
                return update_database(conn, team_id, user_id, new_score, False)
            else:
                raise
    conn.commit()  # TODO: return something


def setup_team(conn, team_id: str):
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE points.%s (
            user_id TEXT PRIMARY KEY,
            score INTEGER NOT NULL DEFAULT 0)""",
            (team_id,)
        )
        cur.execute(
            """INSERT INTO dbo.teams (team_id)
            VALUES (%s)""",
            (team_id,)
        )
    conn.commit()
    user_ids = []
    slack_client = SlackClient(api_token)
    resp = slack_client.api_call(
        'users.list',
        presence=False
    )
    for user in resp['members']:
        if user['deleted'] is False and user['is_bot'] is False:
            user_ids.append(user['id'])
    args_str = ','.join(cur.mogrify("(%s,0)", uid) for uid in user_ids)
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO points.%s (user_id, score)
            VALUES """ + args_str
        )
    # TODO set up event listener for all new users to add, and all removed users to delete


def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE SCHEMA points""")
        cur.execute("""CREATE SCHEMA dbo""")
        cur.execute("""CREATE TABLE dbo.teams (team_id TEXT PRIMARY KEY)""")
    conn.commit()


def main():
    app.run(host='0.0.0.0')
