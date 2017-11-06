from typing import List, Tuple
import os

import psycopg2
from psycopg2.extensions import AsIs
from slackclient import SlackClient

api_token = os.environ.get('POINTY_APP_TOKEN')


def check_score(conn, team_id: str, user_id: str, retry: bool = True) -> int:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """SELECT score FROM points.%s WHERE user_id = %s""",
                (AsIs(team_id), user_id)
            )
            score = cur.fetchone()[0]
        except psycopg2.ProgrammingError:
            conn.rollback()
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
            conn.rollback()
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
            conn.rollback()
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
            (AsIs(team_id),)
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
