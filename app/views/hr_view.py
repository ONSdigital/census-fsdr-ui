from app.employee_view_functions import process_device_details, format_line_manager, extract_device_phone, extract_device_chromebook
from app.tabutils import tab_generation, format_to_uk_dates
from app.fieldmapping import map_employee_name

EMP_INFO_FIELDS = {
    'Unique Employee ID': 'uniqueEmployeeId',
    'Unique Employee ID': 'uniqueEmployeeId',
    'Address': 'address',
    'Postcode': 'postcode',
    'Country': 'country',
    'County': 'county',
    'Personal Email Account': 'personalEmailAddress',
    'Personal Mobile Number': 'telephoneNumberContact1',
    # 'Home Phone Number': 'telephoneNumberContact2',
    'Emergency Contact Name': 'emergencyContactFullName',
    'Emergency Contact Number': 'emergencyContactMobileNo',
    'Mobility': 'mobility',
    'Badge Number': 'idBadgeNo',
    'Weekly Hours': 'weeklyHours',
    'Date of Birth': 'dob',
    'ONS ID': 'onsId',
}

JOB_ROLE_FIELDS = {
    # 'Job Role Type': 'jobRoleType',
    'Job Role': 'jobRole',
    'Job Role ID': 'uniqueRoleId',
    'Job Role Short': 'jobRoleShort',
    'Area Location': 'areaLocation',
    'Assignment Status': 'assignmentStatus',
}

JOB_ROLE_DATE_FIELDS = {
    'Contract Start Date': 'contractStartDate',
    'Contract End Date': 'contractEndDate',
    # 'Operational Start Date': 'contractStartDate',
    # 'Operational End Date': 'operationalEndDate',
}


def get_employee_tabs(employee_info, current_job_role, device_information):
  def get_emp_info(name, on_false={}, on_missing='Unspecified'):
    # This first line is odd, but basically triggers whenever the
    # user did not supply a value for on_false
    if on_false is get_emp_info.__defaults__[0]:
      return employee_info.get(name, on_missing)
    else:
      return employee_info.get(name, on_missing) or on_false

  devices, device_numbers = process_device_details(device_information)
  phone = extract_device_phone(devices)
  chr_book = extract_device_chromebook(devices)

  employee_name = map_employee_name(employee_info)

  preferred_name = get_emp_info('preferredName', on_false='None')

  line_manager = format_line_manager(current_job_role)

  glance_data = {
      'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
      'Name': employee_name,
      'Preferred Name': preferred_name,
      'ONS ID': get_emp_info('onsId'),
      'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
  }
  tab_glance = tab_generation('At a Glance', glance_data)

  employee_data = {
      'Name': employee_name,
      'Preferred Name': preferred_name,
      'Line Manager': line_manager,
      'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
  }
  for mapField, empField in EMP_INFO_FIELDS.items():
    employee_data[mapField] = get_emp_info(empField)
  for mapField, jobField in JOB_ROLE_FIELDS.items():
    employee_data[mapField] = current_job_role.get(jobField)
  for mapField, jobField in JOB_ROLE_DATE_FIELDS.items():
    field = current_job_role.get(jobField)
    employee_data[mapField] = format_to_uk_dates(field)

  tab_employment_status = tab_generation('Employment Status', employee_data)

  all_tabs = [{'all_info': tab_glance + tab_employment_status}]

  return all_tabs
