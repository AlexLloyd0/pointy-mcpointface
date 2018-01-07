import logging
import os

logger = logging.getLevelName(__name__)

CLIENT_ID = os.environ(['CLIENT_ID'])


def redirect_request():
    scope = []
