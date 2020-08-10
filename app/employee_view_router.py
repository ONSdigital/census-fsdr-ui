from app.employee_view_functions import process_employee_information, get_current_job_role
from app.views import rmt_view, hq_fo_ccs_view, logistics_view, hr_view, fsss_view, recruitment_view

import re


area_extraction_regex = re.compile('^..-(...).(-..(-..)?)?$')

def get_employee_tabs(role_id, employee_information, current_job_role, device_information):
    employee_information = process_employee_information(employee_information)

    current_job_role = get_current_job_role(current_job_role)
    area = area_extraction_regex.match(role_id)

    # RMT
    if area == 'RMT':
        return rmt_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # HQ, FO, CCS
    elif area == 'HQO' or area == 'FFO' or area == 'CCS':
        return hq_fo_ccs_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # Logistics
    elif area == 'FLS':
        return logistics_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # HR
    elif area == 'FPH':
        return hr_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # FSSS
    elif area == 'FSS':
        return fsss_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # Recruitiment
    elif area == 'FPR':
        return recruitment_view.get_employee_tabs(employee_information, current_job_role, device_information)
    # Failed to match
    else:
        return []
