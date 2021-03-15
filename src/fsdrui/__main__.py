import os
from aiohttp import web

from .app import create_app

if not os.getenv('APP_SETTINGS'):
  os.environ['APP_SETTINGS'] = 'DevelopmentConfig'

app = create_app()
web.run_app(app, port=app['PORT'])
