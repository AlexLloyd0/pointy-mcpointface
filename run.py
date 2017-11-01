from slackbot.bot import Slackbot
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
    token = os.environ.get('SLACKBOT_POINTY_TOKEN')

    try:
        with open('scores.json', 'r') as file:
            scores = json.load(file)
    except FileNotFoundError:
        with open('scores.json', 'w') as file:
            scores = {}
            json.dump(scores, file)

    bot = Slackbot(token, scores)
    bot.main()
