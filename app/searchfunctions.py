import math

from yarl import URL

from app.utils import FSDR_USER, FSDR_URL, FSDR_PASS
import requests

from requests.auth import HTTPBasicAuth
from app.tabutils import acc_generation
from structlog import get_logger


logger = get_logger('fsdr-ui')


def get_employee_count(user_filter=""):
    employee_record_url = URL(
        FSDR_URL + "/fieldforce/employeeCount/").with_query(
        user_filter
    )
    return requests.get(f'{employee_record_url}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_distinct_job_role_short():
    return requests.get(FSDR_URL + f'/jobRoles/allJobRoleShorts/distinct',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_all_assignment_status():
    return requests.get(FSDR_URL + f'/jobRoles/assignmentStatus',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))

def get_employee_records_no_device(user_filter=""):
    employee_record_url = URL(
        FSDR_URL + f'/fieldforce/byType/byRangeAndUserFilterNoDevice/').with_query(
        user_filter
    )
    return requests.get(employee_record_url,
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_device_records(user_filter=""):
    employee_record_url = URL(
        FSDR_URL + f'/fieldforce/byType/byRangeAndUserFilterDevice/').with_query(
        user_filter
    )
    return requests.get(employee_record_url,
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_records(user_filter="", iat=False):
    employee_record_url = URL(
        FSDR_URL + f'/fieldforce/byType/byRangeAndUserFilter{"Iat/" if iat else "/"}').with_query(
        user_filter
    )

    return requests.get(employee_record_url,
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))

def get_microservice_records(endpoint_name,user_filter=""):
    #TODO remove
    logger.error("ENdpoint name is: " + str(endpoint_name))
    microservice_url = URL(
        FSDR_URL + f'/fieldforce/byMicroservice/{endpoint_name}/').with_query(
        user_filter
    )

    return requests.get(microservice_url,
        verify=False,
        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


# TODO allocate_search_ranges superceeded by pageutils, this should be deleted
async def allocate_search_ranges(user_filter, page_number):
    employee_count = get_employee_count(user_filter)

    max_page = (int(employee_count.text) / 50) - 1
    if page_number >= max_page:
        page_number = int(math.floor(max_page))
    if page_number == 0:
        low_value = 1
        high_value = 50
    elif page_number > 1:
        low_value = 50 * page_number
        high_value = low_value + 50
    else:
        low_value = page_number
        high_value = 50
    return high_value, low_value, page_number, max_page


def employee_table_headers():
    add_headers = [
        {
            'value': 'Badge No',
            'aria_sort': 'none'
        },
        {
            'value': 'Name',
            'aria_sort': 'none'
        },
        {
            'value': 'Job Role ID',
            'aria_sort': 'none'
        },
        {
            'value': 'Job Role',
            'aria_sort': 'none'
        },
        {
            'value': 'Asgmt. Status',
            'aria_sort': 'none'
        }
    ]

    return add_headers


def employee_record_table(employee_records_json):
    add_employees = []
    for employees in employee_records_json:
        add_employees.append({'tds': [
            {
                'value': employees['id_badge_no']
            },
            {
                'value': '<a href="/employeeinformation/' + employees['unique_employee_id'] + '">' +
                         employees['first_name'] + " " + employees['surname'] + '</a>'
            },
            {
                'value': employees['unique_role_id']
            },
            {
                'value': employees['job_role_short']
            },
            {
                'value': employees['assignment_status']
            }
        ]}
        )
    return add_employees

#Below is the layout generator for the interface action table  
#  iat = Interface Action Table

def iat_employee_table_headers():
    add_headers = [
       {
            'value': 'Role ID',
            'aria_sort': 'none'
        },
        {
            'value': 'ONS ID',
            'aria_sort': 'none'
        },
        {
            'value': 'Employee ID',
            'aria_sort': 'none'
        },
        {
            'value': 'Start Date',
            'aria_sort': 'none'
        },

        {
            'value': 'Gsuite',
            'aria_sort': 'none'
        },
        {
            'value': 'XMA',
            'aria_sort': 'none'
        },
        {
            'value': 'Granby',
            'aria_sort': 'none'
        },
        {
            'value': 'Lone Worker',
            'aria_sort': 'none'
        },
        {
            'value': 'Service Now',
            'aria_sort': 'none'
        },
      ]

    return add_headers

def iat_employee_record_table(employee_records_json, remove_html = False):
    add_employees = []
    for employees in employee_records_json:
        add_employees.append({'tds': [
            {
                'value': employees['unique_role_id']
            },
            {
                'value': acc_generation(str(employees['ons_email_address'])) if  not remove_html else str(employees['ons_email_address'])
            },
            {
                'value':  acc_generation(str(employees['external_id']))      if  not remove_html else str(employees['external_id'])
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
       ]}
        )

    return add_employees

# Device Table below
def device_table_headers():
    add_headers = [
        {
            'value': 'Device ID',
            'aria_sort': 'none'
        },
        {
            'value': 'Phone Number',
            'aria_sort': 'none'
        },
        {
            'value': 'Device Type',
            'aria_sort': 'none'
        },
        {
            'value': 'Device  Sent',
            'aria_sort': 'none'
        },
        {
            'value': 'ONS ID',
            'aria_sort': 'none'
        },

      ]

    return add_headers

def device_records_table(device_records_json):
    add_devices = []
    for devices in device_records_json:
        add_devices.append({'tds': [
            {
                'value': devices['device_id']
            },
            {
                'value': devices['field_device_phone_number']
            },
            {
                'value': devices['device_type']
            },
            {
                'value': devices['device_sent'] if (devices['device_sent'] != False) else "False"
            },
            {
                'value': devices['ons_email_address']
            },
       ]}
        )

    return add_devices


