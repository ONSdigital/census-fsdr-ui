from app.employee_view_functions import process_employee_information, get_current_job_role
from app.views import rmt_view, hq_fo_ccs_view, logistics_view, hr_view, fsss_view, recruitment_view

from . import saml, role_matchers


def get_employee_tabs(role_id, employee_information, current_job_role, device_information):
    employee_information = process_employee_information(employee_information)

    cur_job_role = get_current_job_role(current_job_role)

    # RMT
    if role_matchers.rmt_regex.match(role_id):
        return rmt_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # HQ, FO, CCS
    elif role_matchers.hq_fo_ccs_regex.match(role_id):
        return hq_fo_ccs_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # Logistics
    elif role_matchers.logi_regex.match(role_id):
        return logistics_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # HR
    elif role_matchers.hr_regex.match(role_id):
        return hr_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # FSSS
    elif role_matchers.fsss_regex.match(role_id):
        return fsss_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # Recruitiment
    elif role_matchers.recruit_regex.match(role_id):
        return recruitment_view.get_employee_tabs(employee_information, cur_job_role, device_information)
    # Failed to match
    else:
        return []
