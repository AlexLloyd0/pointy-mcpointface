import logging
import os
from urllib import parse

import psycopg2
from flask import Flask, request

from slackbot.add_points import add_points
from slackbot.get_score import get_score
from slackbot.get_scoreboard import get_scoreboard
from slackbot.add_team import add_team

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
    return add_points(form)


@app.route('/get-score', methods=['POST'])
def get_score_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
    return get_score(form)


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
    return get_scoreboard(form)


@app.route('/add-team', methods=['POST'])
def add_team_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':  # TODO
        return
    return add_team(form)


def main():
    app.run(host='0.0.0.0')
