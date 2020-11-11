with open('version.txt', 'r') as file:
    VERSION = file.read().replace('\n', '')


DATABASE_DOWN_MSG = {'text': 'The database appears to be down. Please try again later.', 'clickable': False, 'level': 'ERROR', 'type': 'SYSTEM_RESPONSE_ERROR', 'field': 'no_employee_data'}
INVALID_SIGNIN_MSG = {'title': 'Sign in has failed', 'text': 'Please re-enter your user name and/or password.', 'clickable': True, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'user'}
INVALID_SEARCH_MSG = {'text': 'Please add fsdrsearch criteria.', 'clickable': False, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'fsdrsearch'}
NEED_TO_SIGN_IN_MSG = {'text': 'Please sign in before using website.', 'clickable': True, 'level': 'ERROR', 'type': 'INVALID_CODE', 'field': 'signin_first'}
NO_EMPLOYEE_DATA = {'text': 'No employee records found.', 'clickable': True, 'level': 'ERROR', 'type': 'NO_DATA', 'field': 'no_employee_data'}
SERVICE_DOWN_MSG = {'text': 'Service is temporarily down', 'level': 'ERROR', 'type': 'SERVICE_DOWN_MSG'}
SOMETHING_WENT_WRONG = {'text': 'Something went wrong. Please try again.', 'level': 'ERROR', 'type': 'SOMETHING_WENT_WRONG'}
VALIDATION_FAILURE_MSG = {'text': 'Session timed out or permission denied', 'level': 'ERROR', 'type': 'VALIDATION_FAILURE_MSG', 'field': 'uac'}

import os

from aiohttp import web

if not os.getenv('APP_SETTINGS'):
    os.environ['APP_SETTINGS'] = 'DevelopmentConfig'

if __name__ == '__main__':
    from app.app import create_app
    app = create_app()
    web.run_app(app, port=app['PORT'])

