import requests
from requests.auth import HTTPBasicAuth

from app.utils import FSDR_URL, FSDR_USER, FSDR_PASS
from app.views import rmt_view, hq_fo_ccs_view, logistics_view, hr_view, fsss_view, recruitment_view


def get_employee_tabs(user_role, employee_information, current_job_role, job_roles, device_information):
    for emp_info in employee_information:
        if employee_information[emp_info] is None:
            if emp_info == 'mobility':
                employee_information[emp_info] = 'No'
            elif emp_info == 'mobileStaff':
                employee_information[emp_info] = 'No'
            else:
                employee_information[emp_info] = '-'

    for current_role in current_job_role:
        if current_job_role[current_role] is None:
            current_job_role[current_role] = '-'

    for role in job_roles:
        if job_roles[role] is None:
            job_roles[role] = '-'

    if user_role == 'rmt':
        all_employee_tabs = rmt_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                       device_information)
    elif user_role == 'hq' or user_role == 'fo' or user_role == 'ccs':
        all_employee_tabs = hq_fo_ccs_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                             device_information)
    elif user_role == 'logistics':
        all_employee_tabs = logistics_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                             device_information)
    elif user_role == 'hr':
        all_employee_tabs = hr_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                      device_information)
    elif user_role == 'fsss':
        all_employee_tabs = fsss_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                        device_information)
    elif user_role == 'recruitment':
        all_employee_tabs = recruitment_view.get_employee_tabs(employee_information, current_job_role, job_roles,
                                                               device_information)

    return all_employee_tabs


def employee_devices(device_information):
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
