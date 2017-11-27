import logging
import os

from flask import Flask, request, jsonify

from slackbot.add_points import add_points
from slackbot.add_team import add_team
from slackbot.get_score import get_score
from slackbot.get_scoreboard import get_scoreboard

logger = logging.getLogger(__name__)

app = Flask(__name__)

verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


@app.route('/add-points', methods=['POST'])
def add_points_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/points':
        return "Invalid command"
    return jsonify(add_points(form))


@app.route('/get-score', methods=['POST'])
def get_score_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/score':
        return "Invalid command"
    return jsonify(get_score(form))


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard_route():
    form = request.form
    if form.get('token') != verify_token or form.get('command') != '/leaderboard':
        return "Invalid command"
    return jsonify(get_scoreboard(form))


@app.route('/add-team', methods=['POST'])
def add_team_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Invalid command"
    return jsonify(add_team(form))


@app.route('/action-endpoint', methods=['POST'])
def action_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Invalid command"

    if form.get('type') == 'url_verification':
        return form.get('challenge')


def main():
    app.run(host='0.0.0.0')
