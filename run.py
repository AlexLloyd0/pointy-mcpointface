import slackbot.bot
import os
import json
import logging


def setup_logging():
    logger = logging.getLogger(__name__)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


if __name__ == '__main__':
    setup_logging()
    slackbot.bot.main()
