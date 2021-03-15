from app.fieldmapping import (
    map_employee_history_table_headers,
    map_employee_history_job_role_table_headers,
)


def history_tab(user_role,
                employee_history,
                actual_history,
                employee_history_job_role=None):
  if employee_history_job_role is None:
    employee_history_job_role = []

  # now merge the Employee_history into each dictionarty in actual history
  final_history = []
  for each_history in actual_history:
    temp = {**each_history, **employee_history}
    dictionary_copy = temp.copy()
    final_history.append(dictionary_copy)

  employee_history_information = map_employee_history_table_headers(
      user_role, final_history)

  employee_history_job_role = map_employee_history_job_role_table_headers(
      employee_history_job_role)

  employee_history_tabs = [
      employee_history_information, employee_history_job_role
  ]

  return employee_history_tabs
