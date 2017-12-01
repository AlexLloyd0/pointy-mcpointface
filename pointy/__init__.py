import logging
import os

from flask import Flask, request, jsonify

from pointy.api.add_points import add_points
from pointy.api.add_team import add_team
from pointy.api.add_user import add_user
from pointy.api.get_score import get_score
from pointy.api.get_scoreboard import get_scoreboard
from pointy.setup_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


@app.route('/add-points', methods=['POST'])
def add_points_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Incorrect verification token"
    if form.get('command') != '/points':
        return "Invalid command"
    return jsonify(add_points(form))


@app.route('/get-score', methods=['POST'])
def get_score_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Incorrect verification token"
    if form.get('command') != '/score':
        return "Invalid command"
    return jsonify(get_score(form))


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Incorrect verification token"
    if form.get('command') != '/leaderboard':
        return "Invalid command"
    return jsonify(get_scoreboard(form))


@app.route('/add-team', methods=['POST'])
def add_team_route():
    form = request.form
    if form.get('token') != verify_token:
        return "Incorrect verification token"
    return jsonify(add_team(form))


@app.route('/action-endpoint', methods=['POST'])
def action_route():
    form = request.form
    json = request.get_json(silent=True)
    if form.get('token') != verify_token and json.get('token') != verify_token:
        return "Incorrect verification token"
    if form.get('type') == 'team_join':
        return jsonify(add_user(form))
    if form.get('type') == 'app_uninstalled':
        raise NotImplemented('Uninstalled app')  # TODO
    if json.get('type') == 'url_verification':
        return json.get('challenge')


def main():
    app.run()
