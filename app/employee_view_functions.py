import requests
from requests.auth import HTTPBasicAuth

from app.utils import FSDR_URL, FSDR_USER, FSDR_PASS


def get_current_job_role(current_job_role):
    for current_role in current_job_role:
        if current_job_role[current_role] is None:
            current_job_role[current_role] = '-'

    return current_job_role


def device_details(device_information):
    device_number = ''
    employee_devices = []

    for information in device_information:
        for devices in information:
            for device in devices:
                if devices[device] is None:
                    devices[device] = '-'
            if 'fieldDevicePhoneNumber' in devices:
                if devices['fieldDevicePhoneNumber'] != '-':
                    device_number = devices['fieldDevicePhoneNumber']

    employee_devices.append({
        'Device ID': devices['deviceId'],
        'Device Phone Number': devices['fieldDevicePhoneNumber'],
        'Device Type': devices['deviceType']
    })

    return employee_devices, device_number


def process_job_roles(job_roles):
    for role in job_roles:
        if job_roles[role] is None:
            job_roles[role] = '-'

    return job_roles


def process_employee_information(employee_information):
    for emp_info in employee_information:
        if employee_information[emp_info] is '' or employee_information[emp_info] is None:
            if emp_info == 'mobility':
                employee_information[emp_info] = 'No'
            elif emp_info == 'workRestrictions':
                employee_information[emp_info] = 'None'
            elif emp_info == 'anyLanguagesSpoken':
                employee_information['anyLanguagesSpoken'] = 'None'
            else:
                employee_information[emp_info] = '-'

    return employee_information


def format_line_manager(current_job_role):
    if current_job_role['lineManagerFirstName'] == '-' and current_job_role['lineManagerSurname'] == '-':
        line_manager = '-'
    elif current_job_role['lineManagerFirstName'] == '-':
        line_manager = current_job_role['lineManagerSurname']
    elif current_job_role['lineManagerSurname'] == '-':
        line_manager = current_job_role['lineManagerFirstName']
    else:
        line_manager = current_job_role['lineManagerFirstName'] + ' ' + current_job_role[
            'lineManagerSurname']
    return line_manager


def get_employee_device(employee_id):
    return requests.get(FSDR_URL + f'/devices/byEmployee/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_information(user_role, employee_id):
    return requests.get(FSDR_URL + f'/fieldforce/byId/{user_role}/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_history_information(user_role, employee_id):
    return requests.get(FSDR_URL + f'/fieldforce/historyById/{user_role}/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))
