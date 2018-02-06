from pointy.exceptions import UserNotFound, InvalidIdError
from pointy.utils import validate_id


def check_score(conn, team_id: str, user_id: str) -> int:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT score FROM points.{team_id} WHERE user_id = %s""",
            (user_id,)
        )
        resp = cur.fetchone()
        if not resp:
            raise UserNotFound
        score = resp[0]
    conn.commit()
    # noinspection PyUnboundLocalVariable
    return score


def update_score(conn, team_id: str, user_id: str, new_score: int):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        cur.execute(
            f"""UPDATE points.{team_id}
            SET score = %s
            WHERE user_id = %s""",
            (new_score, user_id)
        )
    conn.commit()


def insert_user(conn, team_id: str, user_id: str, initial_score: int = 0):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    with conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO points.{team_id} (user_id, score)
            VALUES (%s, %s)""",
            (user_id, initial_score)
        )
    conn.commit()
