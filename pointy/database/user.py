from pointy.database.common import execute_query, execute_query_fetchone
from pointy.exceptions import UserNotFound, InvalidIdError
from pointy.utils import validate_id


def check_score(conn, team_id: str, user_id: str) -> int:
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    resp = execute_query_fetchone(conn,
        f"""SELECT score FROM points.{team_id} WHERE user_id = ?""",
        (user_id,)
    )
    if not resp:
        raise UserNotFound(f"User {user_id} not found in scores for team {team_id}")
    score = resp[0]
    # noinspection PyUnboundLocalVariable
    return score


def increase_score(conn, team_id: str, user_id: str, increase: int):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    execute_query(conn,
            f"""UPDATE points.{team_id}
            SET score = score + ?
            WHERE user_id = ?""",
            (increase, user_id)
        )


def insert_user(conn, team_id: str, user_id: str, initial_score: int = 0):
    if not validate_id(team_id):
        raise InvalidIdError(f"{team_id} is not a valid team_id")

    execute_query(conn,
            f"""INSERT INTO points.{team_id} (user_id, score)
            VALUES (?, ?)""",
            (user_id, initial_score)
        )