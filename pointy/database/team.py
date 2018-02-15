import os
import sqlite3
from contextlib import closing
from typing import List, Tuple

from dotenv import load_dotenv
from slackclient import SlackClient

from pointy.database.common import execute_query, execute_query_fetchall
from pointy.exceptions import InvalidIdError
from pointy.utils import validate_id

envfile = '.dev.env' if os.name == 'nt' else '.env'
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", envfile), override=True)

api_token = os.environ.get('POINTY_APP_TOKEN')


def check_all_scores(conn, team_id: str, retry: bool = True) -> List[Tuple[str, int]]:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    try:
        scoreboard = execute_query_fetchall(conn,
                                            f"""SELECT * FROM {team_id}
                                            ORDER BY score DESC""", ())
    except sqlite3.ProgrammingError:
        conn.rollback()
        setup_team(conn, team_id)
        if retry:
            return check_all_scores(conn, team_id, False)
        else:
            raise
    return scoreboard


def check_scores(conn, team_id: str, offset: int, limit: int = 10, retry: bool = True) -> List[Tuple[str, int]]:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    try:
        scoreboard = execute_query_fetchall(conn,
                                            f"""SELECT * FROM {team_id}
                                            WHERE score != 0
                                            ORDER BY score DESC
                                            LIMIT ?
                                            OFFSET ?""",
                                            (str(limit), str(offset)))
    except sqlite3.ProgrammingError:
        conn.rollback()
        setup_team(conn, team_id)
        if retry:
            return check_all_scores(conn, team_id, False)
        else:
            raise
    return scoreboard


def setup_team(conn, team_id: str):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    try:
        execute_query(conn,
                      f"""CREATE TABLE {team_id} (
                      user_id TEXT PRIMARY KEY,
                      score INTEGER NOT NULL DEFAULT 0)""",
                      ())
        execute_query(conn,
                      """INSERT INTO teams (team_id)
                      VALUES (?)""",
                      (team_id,))
    except sqlite3.ProgrammingError:
        conn.rollback()
        raise
    user_ids = []
    slack_client = SlackClient(api_token)
    resp = slack_client.api_call(
        'users.list',
        presence=False
    )
    for user in resp['members']:
        if user['deleted'] is False and user['is_bot'] is False and user['id'] != 'USLACKBOT':
            user_ids.append(user['id'])

    with closing(conn.cursor()) as cur:
        cur.executemany(
            f"""INSERT INTO {team_id} (user_id, score)
            VALUES (?, 0)""", [(user_id,) for user_id in user_ids])
    conn.commit()


def remove_team(conn, team_id: str):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    try:
        execute_query(conn,
                      f"""DROP TABLE {team_id}""", ())
    except sqlite3.ProgrammingError:
        conn.rollback()
    try:
        execute_query(conn,
                      """DELETE FROM teams
                      WHERE team_id = ?""", (team_id,))
    except sqlite3.ProgrammingError:
        conn.rollback()
