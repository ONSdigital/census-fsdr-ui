from app import config
import os

if os.getenv('APP_SETTINGS') == 'DevelopmentConfig':
  FSDR_USER = config.DevelopmentConfig.FSDR_SERVICE_USER
  FSDR_PASS = config.DevelopmentConfig.FSDR_SERVICE_PASS
  FSDR_URL = config.DevelopmentConfig.FSDR_SERVICE_URL
else:
  FSDR_USER = config.ProductionConfig.FSDR_SERVICE_USER
  FSDR_PASS = config.ProductionConfig.FSDR_SERVICE_PASS
  FSDR_URL = config.ProductionConfig.FSDR_SERVICE_URL
