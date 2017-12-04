import logging.config

config = {'disable_existing_loggers': False,
          'formatters': {'screen': {'format': '%(asctime)s - %(name)s - %(levelname)s - '
                                              '%(message)s'}},
          'handlers': {'console': {'class': 'logging.StreamHandler',
                                   'formatter': 'screen',
                                   'level': 'DEBUG',
                                   'stream': 'ext://sys.stdout'}
                       },
          'root': {'handlers': ['console'],
                   'level': 'DEBUG'},
          'version': 1}


def setup_logging():
    logging.config.dictConfig(config)
