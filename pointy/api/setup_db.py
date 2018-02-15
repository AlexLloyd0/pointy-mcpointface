import json
import logging

from flask import Response

from pointy.database.build import build_db
from pointy.database.common import connect

logger = logging.getLogger(__name__)


def setup_db(test: bool):
    logger.debug(f"Building {'test' if test else 'live'} database.")
    with connect(test) as conn:
        build_db(conn)
    return Response(json.dumps({"status": "success"}), 200)
