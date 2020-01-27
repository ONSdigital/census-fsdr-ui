from functools import partial

from envparse import Env, ConfigurationError


class Config(dict):
    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                config = getattr(obj, key)
                if config is None:
                    raise ConfigurationError(f'{key} not set')
                self[key] = config

    def get_service_urls_mapped_with_path(self,
                                          path='/',
                                          suffix='URL',
                                          excludes=None) -> dict:
        return {
            service_name: f'{self[service_name]}{path}'
            for service_name in self
            if service_name.endswith(suffix) and service_name not in (
                excludes if excludes else [])
        }

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f'"{name}" not found')

    def __setattr__(self, name, value):
        self[name] = value


class BaseConfig:
    env = Env()
    env = partial(env, default=None)

    HOST = env('HOST')
    PORT = env('PORT')
    LOG_LEVEL = env('LOG_LEVEL')
    EXT_LOG_LEVEL = env('EXT_LOG_LEVEL')

    DOMAIN_URL_PROTOCOL = env('DOMAIN_URL_PROTOCOL', default='https://')
    DOMAIN_URL = env('DOMAIN_URL')

    JSON_SECRET_KEYS = env('JSON_SECRET_KEYS')

    FSDR_SERVICE_URL = env('FSDR_SERVICE_URL')
    FSDR_SERVICE_URL_AUTH = (env('FSDR_SERVICE_USERNAME'), env('FSDR_SERVICE_PASSWORD'))

    REDIS_SERVER = env('REDIS_SERVER', default='localhost')

    REDIS_PORT = env('REDIS_PORT', default='6379')

    SESSION_AGE = env('SESSION_AGE', default='6000')

    URL_PATH_PREFIX = env('URL_PATH_PREFIX', default='')

class ProductionConfig(BaseConfig):
    pass


class DevelopmentConfig:
    env = Env()
    HOST = env.str('HOST', default='0.0.0.0')
    PORT = env.int('PORT', default='9293')
    LOG_LEVEL = env('LOG_LEVEL', default='INFO')
    EXT_LOG_LEVEL = env('EXT_LOG_LEVEL', default='WARN')

    DOMAIN_URL_PROTOCOL = 'http://'
    DOMAIN_URL = env.str('DOMAIN_URL', default='localhost:9293')

    FSDR_SERVICE_URL = env.str('FSDR_SERVICE_URL', default='http://localhost:5678')
    FSDR_SERVICE_URL_PASS = env.str('FSDR_SERVICE_PASSWORD', default='pass')
    FSDR_SERVICE_URL_USER = env.str('FSDR_SERVICE_USERNAME', default='user')

    REDIS_SERVER = env('REDIS_SERVER', default='localhost')

    REDIS_PORT = env('REDIS_PORT', default='6379')

    SESSION_AGE = env('SESSION_AGE', default='300')  # 5 minutes

    URL_PATH_PREFIX = env('URL_PATH_PREFIX', default='')


class TestingConfig:
    HOST = '0.0.0.0'
    PORT = '9092'
    LOG_LEVEL = 'DEBUG'
    EXT_LOG_LEVEL = 'DEBUG'

    DOMAIN_URL_PROTOCOL = 'http://'
    DOMAIN_URL = 'localhost:9293'

    FSDR_SERVICE_URL = 'http://localhost:9293'

    FSDR_SERVICE_URL = ('user', 'pass')

    REDIS_SERVER = ''

    REDIS_PORT = ''

    SESSION_AGE = ''

    URL_PATH_PREFIX = ''

    SESSION_AGE = ''
