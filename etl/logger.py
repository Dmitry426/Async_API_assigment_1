import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('etl')
