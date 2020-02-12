import requests

from requests.auth import HTTPBasicAuth


def get_employee_count(request, retrieve_count=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_USER']
    fsdr_service_url = request.app['FSDR_SERVICE_URL']

    employee_count_url = fsdr_service_url + "/fieldforce/employeeCount/" + retrieve_count
    return requests.get(f'{employee_count_url}',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_distinct_job_role(request):
    fsdr_service_pass = request.app['FSDR_SERVICE_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_USER']
    fsdr_service_url = request.app['FSDR_SERVICE_URL']

    return requests.get(fsdr_service_url + f'/jobRoles/allJobRoles/distinct',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_all_assignment_status(request):
    fsdr_service_pass = request.app['FSDR_SERVICE_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_USER']
    fsdr_service_url = request.app['FSDR_SERVICE_URL']

    return requests.get(fsdr_service_url + f'/jobRoles/assignmentStatus',
                        verify=False,
                        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))


def get_employee_records(request, low_value, high_value, user_filter=""):
    fsdr_service_pass = request.app['FSDR_SERVICE_PASS']
    fsdr_service_user = request.app['FSDR_SERVICE_USER']
    fsdr_service_url = request.app['FSDR_SERVICE_URL']

    return requests.get(
        fsdr_service_url + f'/fieldforce/byType/byRangeAndUserFilter/?rangeHigh={high_value}&rangeLow={low_value}{user_filter}',
        verify=False,
        auth=HTTPBasicAuth(fsdr_service_user, fsdr_service_pass))
