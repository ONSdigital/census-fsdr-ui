import math

from yarl import URL

from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
import requests
import datetime
import asyncio

from requests.auth import HTTPBasicAuth
from app.tabutils import acc_generation
from structlog import get_logger

logger = get_logger('fsdr-ui')

#Job  Role Short Caching
start_time = datetime.datetime.now()
job_role_lock = asyncio.Lock()
job_role_shorts = []


async def get_job_role_shorts():
  return requests.get(FSDR_URL + f'/jobRoles/allJobRoleShorts/distinct',
                      verify=False,
                      auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


async def get_cached_job_role_shorts():
  async with job_role_lock:
    global job_role_shorts, start_time
    current_time = datetime.datetime.now()
    time_diff = current_time - start_time
    minutes_unitl_refresh = 30
    if (time_diff.seconds >
        (minutes_unitl_refresh * 60)) or (job_role_shorts == []):
      start_time = datetime.datetime.now()
      job_role_shorts = await get_job_role_shorts()

    return job_role_shorts


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


def get_device_records(user_filter=""):
  employee_record_url = URL(FSDR_URL +
                            f'/fieldforce/byType/byRangeAndUserFilterDevice/'
                            ).with_query(user_filter)
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
  add_headers = [{
      'value': 'Badge No',
      'aria_sort': 'none'
  }, {
      'value': 'Name',
      'aria_sort': 'none'
  }, {
      'value': 'Job Role ID',
      'aria_sort': 'none'
  }, {
      'value': 'Job Role',
      'aria_sort': 'none'
  }, {
      'value': 'Asgmt. Status',
      'aria_sort': 'none'
  }]

  return add_headers


def employee_record_table(employee_records_json):

  add_employees = []
  for employees in employee_records_json:
    add_employees.append({
        'tds': [{
            'value': employees['id_badge_no']
        }, {
            'value':
            '<a href="/employeeinformation/' +
            employees['unique_employee_id'] + '">' + employees['first_name'] +
            " " + employees['surname'] + '</a>'
        }, {
            'value': employees['unique_role_id']
        }, {
            'value': employees['job_role_short']
        }, {
            'value': employees['assignment_status']
        }]
    })
  return add_employees


def iat_employee_record_table(employee_records_json, remove_html=False):
  add_employees = []
  for employees in employee_records_json:
    add_employees.append({
        'tds': [
            {
                'value': employees['unique_role_id']
            },
            {
                'value':
                acc_generation(str(employees['ons_email_address']))
                if not remove_html else str(employees['ons_email_address'])
            },
            {
                'value':
                acc_generation(str(employees['external_id']))
                if not remove_html else str(employees['external_id'])
            },
            {
                'value': employees['contract_start_date']
            },
            {
                'value': employees['gsuite_status']
            },
            {
                'value': employees['xma_status']
            },
            {
                'value': employees['granby_status']
            },
            {
                'value': employees['lone_worker_solution_status']
            },
            {
                'value': employees['service_now_status']
            },
            {
                'value': "True" if (employees['setup'] == "t") else "False"
            },
        ]
    })

  return add_employees
