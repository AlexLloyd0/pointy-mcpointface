from psycopg2.extensions import AsIs

from slackbot.exceptions import UserNotFound


def check_score(conn, team_id: str, user_id: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """SELECT score FROM points.%s WHERE user_id = %s""",
            (AsIs(team_id), user_id)
        )
        resp = cur.fetchone()
        if not resp:
            raise UserNotFound
        score = resp[0]
    conn.commit()
    return score


def update_score(conn, team_id: str, user_id: str, new_score: int):
    with conn.cursor() as cur:
        cur.execute(
            """UPDATE points.%s
            SET score = %s
            WHERE user_id = %s""",
            (AsIs(team_id), new_score, user_id)
        )
    conn.commit()  # TODO: return something


def add_user(conn, team_id: str, user_id: str, initial_score: int = 0):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO points.%s (user_id, initial_score)
            VALUES (%s, %s)""",
            (AsIs(team_id), user_id, initial_score)
        )
    conn.commit()  # TODO: return something
