from app.employee_view_functions import process_employee_information, map_false_to_dash
from app.views import rmt_view, hq_fo_ccs_view, logistics_view, hr_view, fsss_view, recruitment_view

from . import role_matchers


def get_employee_tabs(role_id, employee_information, current_job_role, device_information):
    employee_information = process_employee_information(employee_information)

    cur_job_role = map_false_to_dash(current_job_role)

    get_employee_tabs = role_matchers.role_id_to_view_router(role_id)

    return get_employee_tabs(employee_information, cur_job_role, device_information)
