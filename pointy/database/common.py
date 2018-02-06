import logging
import os
from typing import Dict, List
from urllib import parse

import pymysql
from dotenv import load_dotenv

envfile = '.dev.env' if os.name == 'nt' else '.env'
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", envfile), override=True)

parse.uses_netloc.append("postgres")

RDS_HOST = os.environ.get("DB_HOST")
RDS_PORT = int(os.environ.get("DB_PORT", 3306))
NAME = os.environ.get("DB_USERNAME")
PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

logger = logging.getLogger(__name__)


def setup_db(conn):
    with conn.cursor() as cur:
        cur.execute("""CREATE SCHEMA points""")
        cur.execute("""CREATE SCHEMA dbo""")
        cur.execute("""CREATE TABLE dbo.teams (team_id TEXT PRIMARY KEY)""")
    conn.commit()


def connect():
    logger.debug(f"Connecting to {RDS_HOST}")
    return pymysql.connect(host=RDS_HOST,
                           user=NAME,
                           passwd=PASSWORD,
                           port=RDS_PORT,
                           cursorclass=pymysql.cursors.DictCursor,
                           )


def ephemeral_resp(text: str, attachments: List[Dict] = None) -> Dict[str, str]:
    if not attachments:
        attachments = []
    logger.debug(f"Ephemeral response{' (with attachments)' if attachments else ''}: {text}")
    resp = {
        "response_type": "ephemeral",
        "text": text
    }
    if attachments:
        resp["attachments"] = attachments
    return resp


def channel_resp(text: str, attachments: List[Dict] = None) -> Dict[str, str]:
    if not attachments:
        attachments = []
    logger.debug(f"Channel response{' (with attachments)' if attachments else ''}: {text}")
    resp = {
        "response_type": "in_channel",
        "text": text
    }
    if attachments:
        resp["attachments"] = attachments
    return resp
