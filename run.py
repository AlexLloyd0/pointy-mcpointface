import slackbot.bot
import yaml
import logging.config


def setup_logging():
    with open('logging.yaml', 'rt') as log_file:
        config = yaml.safe_load(log_file.read())
    logging.config.dictConfig(config)


if __name__ == '__main__':
    setup_logging()
    slackbot.bot.main()
