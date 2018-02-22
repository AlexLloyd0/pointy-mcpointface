import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Dict, List

DB_LOCATION = Path('data')

logger = logging.getLogger(__name__)


def connect(test=False):
    logger.debug(f"Connecting to SQLite")
    path = DB_LOCATION / 'test.db' if test else DB_LOCATION / 'live.db'
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(conn, query, parameters):
    with closing(conn.cursor()) as cur:
        cur.execute(query, parameters)
    conn.commit()


def execute_query_fetchone(conn, query, parameters):
    with closing(conn.cursor()) as cur:
        cur.execute(query, parameters)
        result = cur.fetchone()
    conn.commit()
    return result


def execute_query_fetchall(conn, query, parameters):
    with closing(conn.cursor()) as cur:
        cur.execute(query, parameters)
        result = cur.fetchall()
    conn.commit()
    return result


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
