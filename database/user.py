import psycopg2

from psycopg2.extensions import AsIs
from slackbot.exceptions import UserNotFound

from database.team import setup_team


def check_score(conn, team_id: str, user_id: str, retry: bool = True) -> int:
    with conn.cursor() as cur:
        try:
            cur.execute(
                """SELECT score FROM points.%s WHERE user_id = %s""",
                (AsIs(team_id), user_id)
            )
            resp = cur.fetchone()
            if not resp:
                raise UserNotFound
            score = resp[0]
        except psycopg2.ProgrammingError:
            conn.rollback()
            setup_team(conn, team_id)
            if retry:
                return check_score(conn, team_id, user_id, False)
            else:
                raise
    conn.commit()
    return score


def update_score(conn, team_id: str, user_id: str, new_score: int, retry: bool = True) -> bool:
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
                return update_score(conn, team_id, user_id, new_score, False)
            else:
                raise
    conn.commit()  # TODO: return something
