import json
import logging
import os

from flask import Flask, request, jsonify

from pointy.api.add_points import add_points
from pointy.api.add_team import add_team
from pointy.api.add_user import add_user
from pointy.api.get_score import get_score
from pointy.api.get_scoreboard import get_scoreboard, get_scoreboard_page
from pointy.api.setup_db import setup_db
from pointy.setup_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

verify_token = os.environ.get('POINTY_VERIFY_TOKEN')


@app.route('/add-points', methods=['POST'])
def add_points_route():
    form = request.form
    logger.debug(f"/add-points request: {form}")
    if form.get('token') != verify_token:
        return "Incorrect verification token", 403
    if form.get('command') != '/points':
        return "Invalid command"
    return jsonify(add_points(form))


@app.route('/get-score', methods=['POST'])
def get_score_route():
    form = request.form
    logger.debug(f"/get-score request: {form}")
    if form.get('token') != verify_token:
        return "Incorrect verification token", 403
    if form.get('command') != '/score':
        return "Invalid command"
    return jsonify(get_score(form))


@app.route('/get-scoreboard', methods=['POST'])
def get_scoreboard_route():
    form = request.form
    logger.debug(f"/get-scoreboard request: {form}")
    if form.get('token') != verify_token:
        return "Incorrect verification token", 403
    if form.get('command') != '/leaderboard':
        return "Invalid command"
    return jsonify(get_scoreboard_page(form, offset=0))


@app.route('/add-team', methods=['POST'])
def add_team_route():
    form = request.form
    logger.debug(f"/add-team request: {form}")
    if form.get('token') != verify_token:
        return "Incorrect verification token", 403
    return jsonify(add_team(form))


@app.route('/event-endpoint', methods=['POST'])
def action_route():
    form = request.form
    logger.debug(f"/event-endpoint request: {form}")
    # json_ is only for url verification
    json_ = request.get_json(silent=True)
    if form.get('token') != verify_token and json_.get('token') != verify_token:
        return "Incorrect verification token", 403
    if form.get('type') == 'team_join':
        return jsonify(add_user(form))
    if form.get('type') == 'app_uninstalled':
        raise NotImplemented('Uninstalled app')  # TODO
    if json_.get('type') == 'url_verification':
        return jsonify({'challenge': json_.get('challenge')})


@app.route('/interactive-endpoint', methods=['POST'])
def interactive_route():
    form = request.form
    logger.debug(f"/interactive-endpoint request: {form}")
    payload = form.get('payload', {})
    try:
        form = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return "Malformed payload", 400
    if form.get('token') != verify_token:
        return "Incorrect verification token", 403
    if form.get('callback_id') == 'leader_scroll':
        return jsonify(get_scoreboard_page(form))
    logger.info(str(form))


@app.route('/oauth-redirect', methods=[''])
def oauth_redirect():
    pass


def main():
    app.run()
