from app.employee_view_functions import process_employee_information, map_false_to_dash

from . import views
from .role_matchers import RoleEnum, get_role


def role_to_router(role):
  view_map = {
      RoleEnum.RMT: views.rmt_view,
      RoleEnum.LOGISTICS: views.logistics_view,
      RoleEnum.FSSS: views.fsss_view,
      RoleEnum.HR: views.hr_view,
  }
  return view_map[role]


def get_employee_tabs(role_id, employee_info, current_job_role, device_info):
  role = get_role(role_id)

  employee_info = process_employee_information(employee_info)

  cur_job_role = map_false_to_dash(current_job_role)

  router = role_to_router(role)

  return router.get_employee_tabs(employee_info, cur_job_role, device_info)
