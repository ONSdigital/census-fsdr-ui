import requests
from requests.auth import HTTPBasicAuth

from app.utils import FSDR_URL, FSDR_USER, FSDR_PASS
from . import role_matchers


def get_current_job_role(current_job_role):
    for current_role in current_job_role:
        if current_job_role[current_role] is None:
            current_job_role[current_role] = '-'

    return current_job_role


def device_details(device_information):
    device_number = ''
    employee_devices = []

    # TODO: There are never more than one of these. Simplify.
    for devices in device_information:
        for device in devices:
            for field in device:
                if device[field] is None:
                    device[field] = '-'
            if 'fieldDevicePhoneNumber' in device and device['fieldDevicePhoneNumber'] != '-':
                device_number = device['fieldDevicePhoneNumber']

            employee_devices.append({
                'Device ID': device['deviceId'],
                'Device Phone Number': device['fieldDevicePhoneNumber'],
                'Device Type': device['deviceType']
            })

    return employee_devices, device_number


def process_job_roles(job_roles):
    for role in job_roles:
        if job_roles[role] is None:
            job_roles[role] = '-'

    return job_roles


def process_employee_information(employee_information):
    for emp_info in employee_information:
        if employee_information[emp_info] is '' or employee_information[
                emp_info] is None:
            if emp_info == 'mobility':
                employee_information[emp_info] = 'No'
            elif emp_info == 'workRestrictions':
                employee_information[emp_info] = 'None'
            else:
                employee_information[emp_info] = '-'

    return employee_information


def format_line_manager(current_job_role):
    maybe_names = (current_job_role['lineManagerFirstName'],
            current_job_role['lineManagerSurname'])
    names = (n for n in maybe_names if n != '-')
    return ' '.join(name) or '-'


def get_employee_device(employee_id):
    return requests.get(FSDR_URL + f'/devices/byEmployee/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_information(user_role, employee_id):
    extract_type = role_matchers.role_id_to_extract_type(user_role)
    return requests.get(FSDR_URL +
                        f'/fieldforce/byId/{extract_type}/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_history_information(user_role, employee_id):
    extract_type = role_matchers.role_id_to_extract_type(user_role)
    return requests.get(
        FSDR_URL + f'/fieldforce/historyById/{extract_type}/{employee_id}',
        verify=False,
        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))
