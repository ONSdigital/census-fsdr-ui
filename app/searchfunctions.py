import math

from yarl import URL

from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
import requests

from requests.auth import HTTPBasicAuth
from app.tabutils import acc_generation
from structlog import get_logger

logger = get_logger('fsdr-ui')


def get_distinct_job_role_short():
  return requests.get(FSDR_URL + f'/jobRoles/allJobRoleShorts/distinct',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_all_assignment_status():
  return requests.get(FSDR_URL + f'/jobRoles/assignmentStatus',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_records_no_device(user_filter=""):
  employee_record_url = URL(FSDR_URL +
                            f'/fieldforce/byType/byRangeAndUserFilterNoDevice/'
                            ).with_query(user_filter)
  return requests.get(employee_record_url,
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_records(user_filter=""):
  employee_record_url = URL(
      FSDR_URL +
      f'/fieldforce/byType/byRangeAndUserFilter/').with_query(user_filter)
  return requests.get(employee_record_url,
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_microservice_records(endpoint_name, user_filter=""):
  microservice_url = URL(
      FSDR_URL +
      f'/fieldforce/byMicroservice/{endpoint_name}/').with_query(user_filter)

  return requests.get(microservice_url,
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def employee_table_headers():
  add_headers = [
      {
          'value': 'Badge No',
          'aria_sort': 'none',
      },
      {
          'value': 'Name',
          'aria_sort': 'none',
      },
      {
          'value': 'Job Role ID',
          'aria_sort': 'none',
      },
      {
          'value': 'Job Role',
          'aria_sort': 'none',
      },
      {
          'value': 'Asgmt. Status',
          'aria_sort': 'none',
      },
  ]

  return add_headers


def employee_record_table(employee_records_json):
  add_employees = []
  for employees in employee_records_json:
    add_employees.append({
        'tds': [
            {
                'value': employees['id_badge_no'],
            },
            {
                'value':
                '<a href="/employeeinformation/' +
                employees['unique_employee_id'] + '">' +
                employees['first_name'] + " " + employees['surname'] + '</a>',
            },
            {
                'value': employees['unique_role_id'],
            },
            {
                'value': employees['job_role_short'],
            },
            {
                'value': employees['assignment_status'],
            },
        ]
    })
  return add_employees
