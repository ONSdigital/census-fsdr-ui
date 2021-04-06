import math

from yarl import URL

from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
import requests

from requests.auth import HTTPBasicAuth
from structlog import get_logger

logger = get_logger('fsdr-ui')


#TODO this can probably be removed. Probably.
def get_employee_records_no_device(user_filter=""):
  employee_record_url = URL(FSDR_URL +
                            f'/fieldforce/byType/byRangeAndUserFilterNoDevice/'
                            ).with_query(user_filter)
  return requests.get(employee_record_url,
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_customsql_records(all_input):
  user_filter = {'rangeHigh': 50, 'rangeLow': 0}

  url = URL(FSDR_URL +
            f'/fieldforce/byMicroservice/customsql/').with_query(user_filter)

  return requests.post(url,
                       verify=False,
                       json=all_input,
                       auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_microservice_records(endpoint_name, user_filter=""):
  endpoint_name = 'index' if endpoint_name == 'search' else endpoint_name
  microservice_url = URL(
      FSDR_URL +
      f'/fieldforce/byMicroservice/{endpoint_name}/').with_query(user_filter)

  return requests.get(microservice_url,
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))
