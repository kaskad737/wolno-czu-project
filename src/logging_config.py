dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base': {
            'format': '%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(lineno)-4d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'base'
        }
    },
    'loggers': {
        'wolnoLogger': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}