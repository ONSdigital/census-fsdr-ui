import json
from app.employee_view_functions import process_device_details, format_line_manager, extract_device_phone, extract_device_chromebook
from app.tabutils import tab_generation, table_generation, format_to_uk_dates
from app.fieldmapping import map_employee_name, map_full_address_details
from app.searchfunctions import get_microservice_records
from structlog import get_logger

logger = get_logger('fsdr-ui')

JOB_ROLE_DATE_FIELDS = {
    'Contract Start Date': 'contractStartDate',
    'Contract End Date': 'contractEndDate',
    'Operational Start Date': 'contractStartDate',
    'Operational End Date': 'operationalEndDate',
}

EMP_JOB_ROLE_FIELDS = {
    'Postcode': 'postcode',
    'County': 'county',
    'Country': 'country',
    'Mobility': 'mobility',
    'Weekly Hours': 'weeklyHours',
}

EMP_CONTACT_FIELDS = {
    'Personal Mobile Number': 'telephoneNumberContact1',
    'Home Phone Number': 'telephoneNumberContact2',
    'Personal Email Account': 'personalEmailAddress',
    'Emergency Contact Name': 'emergencyContactFullName',
    'Emergency Contact Number': 'emergencyContactMobileNo',
}


def get_device_types(devices):
  types_of_device = ""
  if devices != []:
    for device in devices:
      types_of_device = types_of_device + str(device['Device Type']) + "\n"
  return types_of_device if types_of_device != "" else "-"


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

  line_manager = format_line_manager(current_job_role)

  employee_name = map_employee_name(employee_info)

  preferred_name = get_emp_info('preferredName', on_false='None')

  gsuite_filter = {
      'rangeHigh': 10,
      'rangeLow': 0,
      'unique_employee_id': get_emp_info('uniqueEmployeeId'),
  }

  get_microservice_info = get_microservice_records('gsuitetable',
                                                   user_filter=gsuite_filter)
  if str(get_microservice_info.status_code) == '200':
    gsuite_info = get_microservice_info.json()
    if len(gsuite_info) > 0:
      gsuite_info = gsuite_info[0]
    else:
      gsuite_info = {}
  else:
    gsuite_info = {}

  data_detail = {
      'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
      'Name': employee_name,
      'Preferred Name': preferred_name,
      # Gender refferenced here in GUI designs, but not in required Excel spreadsheet, therefore ignored
      'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
      'ONS ID': get_emp_info('onsId'),  #This is Email address
  }
  tab_detail = tab_generation('Details for Field Worker', data_detail)

  data_employment = {
      'Assignment Status': current_job_role.get('assignmentStatus'),
      # "Status" in GUI here
      # "Ingest date" in GUI here
  }
  for mapField, jobField in JOB_ROLE_DATE_FIELDS.items():
    field = current_job_role.get(jobField)
    data_employment[mapField] = format_to_uk_dates(field)

  tab_employment = tab_generation('Employment Status', data_employment)

  data_job_role = {
      'Job Role ID': current_job_role.get('uniqueRoleId'),
      'Job Role Short': current_job_role.get('jobRoleShort'),
      'Job Role': current_job_role.get('jobRole'),
      # device build
      'Line Manager': line_manager,
      # Area Location
      # Area group
      # Coordinator group
      # Organisation unit
  }
  for mapField, empField in EMP_JOB_ROLE_FIELDS.items():
    data_job_role[mapField] = get_emp_info(empField)
  tab_job_role = tab_generation('Job Role for Field Worker', data_job_role)

  data_contact = {
      'Address': map_full_address_details(employee_info),
  }

  for mapField, empField in EMP_CONTACT_FIELDS.items():
    data_contact[mapField] = get_emp_info(empField)
  tab_contact = tab_generation('Personal Contact Details', data_contact)

  data_devices = {
      'Mobile Asset ID': (phone and phone['Device ID']) or None,
      # Device phone number
      'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
      'Chromebook Asset ID': (chr_book and chr_book['Device ID']) or None,
      'Device Type': get_device_types(devices),
  }
  tab_devices = tab_generation('Devices for Field Worker', data_devices)

  data_other = {
      'Job Role Type': current_job_role.get('jobRoleType'),
      'Badge Number': get_emp_info('idBadgeNo'),
      'Gsuite Groups': gsuite_info.get('current_groups', '-'),
      # Unused fields:
      #'Status': get_emp_info('status'),
      #'Coordinator Group': current_job_role.get('coordGroup'),
      #'Organisation Unit': current_job_role.get('uniqueRoleId'),
      #'Ingest Date': get_emp_info('ingestDate'),
      #        'Device Type': device_information[0]['Device Type'], # This doesn't make any sense
  }
  tab_other = tab_generation('Other Data', data_other)

  tabs_all = [{
      'all_info':
      tab_detail + tab_employment + tab_job_role + tab_contact + tab_devices +
      tab_other
  }]
  return tabs_all
