import yaml
import logging.config
import os


def setup_logging():
    with open(os.path.join('..', 'logging.yaml'), 'rt') as log_file:
        config = yaml.safe_load(log_file.read())
    logging.config.dictConfig(config)