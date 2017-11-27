import logging.config
import os

import yaml

file_handler = {"infofilehandler":
    {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "DEBUG",
        "formatter": "screen",
        "filename": "logs // info.log",
        "maxBytes": 10485760,  # 10MB
        "backupCount": 20,
        "encoding": "utf8"
    }}


def setup_logging():
    with open('logging.yaml', 'rt') as log_file:
        config = yaml.safe_load(log_file.read())
    if os.name == 'nt':
        config['handlers'].append(file_handler)
        config['root']['handlers'].append('infofilehandler')
    logging.config.dictConfig(config)
