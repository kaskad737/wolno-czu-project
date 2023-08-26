import logging
import logging.handlers
from master_config import LOGS_PATH

class DebugAndInfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('INFO', 'DEBUG')


class ErrorsFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'


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
        },
        'infoLog': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'base',
            'filename': LOGS_PATH,
            'mode': 'a',
            'filters': ['debug_and_info_filter']
        },
        'errorLog': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'base',
            'filename': LOGS_PATH,
            'mode': 'a',
            'filters': ['errors_filter']
        },
    },
    'loggers': {
        'wolnoLogger': {
            'level': 'DEBUG',
            'handlers': ['console', 'infoLog', 'errorLog']
        }
    },
    'filters': {
        'debug_and_info_filter': {
            '()': DebugAndInfoFilter
        },
        'errors_filter': {
            '()': ErrorsFilter
        }
    }
}