import logging
import os
from typing import Dict
from urllib import parse

import psycopg2

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ["DATABASE_URL"])

logger = logging.getLogger(__name__)


def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE SCHEMA points""")
        cur.execute("""CREATE SCHEMA dbo""")
        cur.execute("""CREATE TABLE dbo.teams (team_id TEXT PRIMARY KEY)""")
    conn.commit()


def connect():
    return psycopg2.connect(database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port)


def ephemeral_resp(text: str) -> Dict[str, str]:
    logger.debug(f"Ephemeral response: {text}")
    return {
        "response_type": "ephemeral",
        "text": text
    }


def channel_resp(text: str) -> Dict[str, str]:
    logger.debug(f"Channel response: {text}")
    return {
        "response_type": "in_channel",
        "text": text
    }
