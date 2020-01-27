import requests

from requests.auth import HTTPBasicAuth

employee_count_base_url = "http://localhost:5678/fieldforce/employeeCount/"


def get_employee_count(request, retrieve_count=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']

    employee_count_url = employee_count_base_url + retrieve_count
    return requests.get(f'{employee_count_url}',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_distinct_job_role(request):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(f'http://localhost:5678/jobRoles/allJobRoles/distinct',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_all_assignment_status(request):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(f'http://localhost:5678/jobRoles/assignmentStatus',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_employee_records(request, low_value, high_value, user_filter=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_URL_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_URL_USER']
    return requests.get(
        f'http://localhost:5678/fieldforce/byType/byRangeAndUserFilter/?rangeHigh={high_value}&rangeLow={low_value}{user_filter}',
        verify=False,
        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))
