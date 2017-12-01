import logging.config

config = {'disable_existing_loggers': False,
          'formatters': {'screen': {'format': '%(asctime)s - %(name)s - %(levelname)s - '
                                              '%(message)s'}},
          'handlers': {'console': {'class': 'logging.StreamHandler',
                                   'formatter': 'screen',
                                   'level': 'DEBUG',
                                   'stream': 'ext://sys.stdout'},
                       "infofilehandler":
                           {
                               "class": "logging.handlers.RotatingFileHandler",
                               "level": "DEBUG",
                               "formatter": "screen",
                               "filename": "logs//info.log",
                               "maxBytes": 10485760,  # 10MB
                               "backupCount": 20,
                               "encoding": "utf8"
                           }
                       },
          'root': {'handlers': ['console', 'infofilehandler'],
                   'level': 'DEBUG'},
          'version': 1}


def setup_logging():
    logging.config.dictConfig(config)
