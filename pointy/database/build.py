
import logging

from pointy.database.common import execute_query

logger = logging.getLogger(__name__)


def build_db(conn):
    execute_query(conn, "CREATE TABLE teams (team_id varchar(20) NOT NULL, PRIMARY KEY (team_id))", ())
