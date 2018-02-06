import os
from typing import List, Tuple

import pymysql
from dotenv import load_dotenv
from slackclient import SlackClient

from pointy.exceptions import InvalidIdError
from pointy.utils import validate_id

envfile = '.dev.env' if os.name == 'nt' else '.env'
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", envfile), override=True)

api_token = os.environ.get('POINTY_APP_TOKEN')


def check_all_scores(conn, team_id: str, retry: bool = True) -> List[Tuple[str, int]]:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        try:
            cur.execute(
                f"""SELECT * FROM points.{team_id}
                ORDER BY score DESC""",
                ()
            )
            scoreboard = cur.fetchall()
        except pymysql.ProgrammingError:
            conn.rollback()
            setup_team(conn, team_id)
            if retry:
                return check_all_scores(conn, team_id, False)
            else:
                raise
    conn.commit()
    return scoreboard


def check_scores(conn, team_id: str, offset: int, limit: int = 10, retry: bool = True) -> List[Tuple[str, int]]:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        try:
            cur.execute(
                f"""SELECT * FROM points.{team_id}
                ORDER BY score DESC
                LIMIT %s
                OFFSET %s""",
                (str(limit), str(offset))
            )
            scoreboard = cur.fetchall()
        except pymysql.ProgrammingError:
            conn.rollback()
            setup_team(conn, team_id)
            if retry:
                return check_all_scores(conn, team_id, False)
            else:
                raise
    conn.commit()
    return scoreboard


def setup_team(conn, team_id: str):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        try:
            cur.execute(
                f"""CREATE TABLE points.{team_id} (
                user_id TEXT PRIMARY KEY,
                score INTEGER NOT NULL DEFAULT 0)""",
                ()
            )
        except pymysql.ProgrammingError:
            pass
        try:
            cur.execute(
                """INSERT INTO dbo.teams (team_id)
                VALUES (%s)""",
                (team_id,)
            )
        except pymysql.ProgrammingError:
            pass
    conn.commit()
    user_ids = []
    slack_client = SlackClient(api_token)
    resp = slack_client.api_call(
        'users.list',
        presence=False
    )
    for user in resp['members']:
        if user['deleted'] is False and user['is_bot'] is False and user['id'] != 'USLACKBOT':
            user_ids.append(user['id'])

    with conn.cursor() as cur:
        cur.executemany(
            f"""INSERT INTO points.{team_id} (user_id, score)
            VALUES (%s, 0)""", (user_ids,)
        )


def remove_team(conn, team_id: str):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        try:
            cur.execute(
                f"""DROP TABLE points.{team_id}""",
                ()
            )
        except pymysql.ProgrammingError:
            conn.rollback()
        try:
            cur.execute(
                """DELETE FROM dbo.teams
                WHERE team_id = %s""",
                (team_id,)
            )
        except pymysql.ProgrammingError:
            conn.rollback()
    conn.commit()
