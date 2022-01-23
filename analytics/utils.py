# coding=utf-8

USER_TYPES = {
    1: 'New',
    None: 'Returning'
}

ERRORS = {
    'ERR01': {
        'CATEGORY': 'Instantiation Error',
        'DESCRIPTION': None
    },
    'ERR02': {
        'CATEGORY': 'BigQuery Error',
        'DESCRIPTION': 'No rows returned for query'
    },
    'ERR03': {
        'CATEGORY': 'Validation Error',
        'DESCRIPTION': 'Provided date not available'
    },

    'ERR04': {
        'CATEGORY': 'CSV Error',
        'DESCRIPTION': None
    }
}
