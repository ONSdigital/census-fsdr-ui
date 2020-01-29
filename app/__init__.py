VERSION = '0.0.1'


BAD_CODE_MSG = {'text': 'Enter your access code.', 'clickable': True, 'level': 'ERROR', 'type': 'BAD_CODE', 'field': 'uac'}
BAD_CODE_TYPE_MSG = {'text': 'Please re-enter your access code and try again.', 'clickable': True, 'level': 'ERROR', 'type': 'NOT_HOUSEHOLD_CODE', 'field': 'uac'}  # NOQA
BAD_RESPONSE_MSG = {'text': 'There was an error, please enter your access code and try again.', 'clickable': True, 'level': 'ERROR', 'type': 'SYSTEM_RESPONSE_ERROR', 'field': 'uac'}  # NOQA
DATABASE_DOWN_MSG = {'text': 'The database appears to be down. Please try again later.', 'clickable': False, 'level': 'ERROR', 'type': 'SYSTEM_RESPONSE_ERROR', 'field': 'no_employee_data'}
INVALID_SIGNIN_MSG = {'title': 'Sign in has failed', 'text': 'Please re-enter your user name and/or password.', 'clickable': True, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'user'}
INVALID_SEARCH_MSG = {'text': 'Please add search criteria.', 'clickable': False, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'search'}
NEED_TO_SIGN_IN_MSG = {'text': 'Please sign in before using website.', 'clickable': True, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'signin_first'}
NO_EMPLOYEE_DATA = {'text': 'No employee records found.', 'clickable': True, 'level': 'ERROR', 'type': 'NO_DATA', 'field': 'no_employee_data'}
NOT_AUTHORIZED_MSG = {'text': 'There was a problem connecting to this study. Please try again later.', 'level': 'ERROR', 'type': 'SYSTEM_AUTH_ERROR', 'field': 'uac'}  # NOQA
SESSION_TIMEOUT_MSG = {'text': 'Apologies, your session has timed out. Please re-enter your access code.', 'level': 'ERROR', 'type': 'SYSTEM_AUTH_ERROR', 'field': 'uac'}  # NOQA
SESSION_TIMEOUT_CODE_MSG = {'text': 'Apologies, your session has timed out. You will need to start again.', 'level': 'ERROR', 'type': 'SYSTEM_AUTH_ERROR', 'field': 'code'}  # NOQA
VALIDATION_FAILURE_MSG = {'text': 'Session timed out or permission denied', 'level': 'ERROR', 'type': 'VALIDATION_FAILURE_MSG', 'field': 'uac'}
SERVICE_DOWN_MSG = {'text': 'Service is temporarily down', 'level': 'ERROR', 'type': 'SERVICE_DOWN_MSG'}
