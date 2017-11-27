import logging.config
import os

import yaml


def setup_logging():
    with open('logging.yaml', 'rt') as log_file:
        config = yaml.safe_load(log_file.read())
    if os.name == 'nt':
        config['root']['handlers'].append('infofilehandler')
    logging.config.dictConfig(config)
