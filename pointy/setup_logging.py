import logging.config

import yaml


def setup_logging():
    with open('logging.yaml', 'rt') as log_file:
        config = yaml.safe_load(log_file.read())
    logging.config.dictConfig(config)
