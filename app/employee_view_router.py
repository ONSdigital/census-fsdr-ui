from app.employee_view_functions import process_employee_information, get_current_job_role
from app.views import rmt_view, hq_fo_ccs_view, logistics_view, hr_view, fsss_view, recruitment_view


def get_employee_tabs(user_role, employee_information, current_job_role, device_information):

    employee_information = process_employee_information(employee_information)

    current_job_role = get_current_job_role(current_job_role)

    if user_role == 'rmt':
        all_employee_tabs = rmt_view.get_employee_tabs(employee_information, current_job_role,
                                                       device_information)
    elif user_role == 'hq' or user_role == 'fo' or user_role == 'ccs':
        all_employee_tabs = hq_fo_ccs_view.get_employee_tabs(employee_information, current_job_role,
                                                             device_information)
    elif user_role == 'logistics':
        all_employee_tabs = logistics_view.get_employee_tabs(employee_information, current_job_role,
                                                             device_information)
    elif user_role == 'hr':
        all_employee_tabs = hr_view.get_employee_tabs(employee_information, current_job_role,
                                                      device_information)
    elif user_role == 'fsss':
        all_employee_tabs = fsss_view.get_employee_tabs(employee_information, current_job_role,
                                                        device_information)
    elif user_role == 'recruitment':
        all_employee_tabs = recruitment_view.get_employee_tabs(employee_information, current_job_role,
                                                               device_information)
    else:
        all_employee_tabs = []

    return all_employee_tabs
