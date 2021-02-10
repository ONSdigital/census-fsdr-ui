from app.tabutils import table_generation, format_to_uk_dates

from . import role_matchers


def map_employee_history_table_headers(user_role, full_history):
  mapping_entries = []

  for history in full_history:
    if role_matchers.fsss_combined_regex.match(user_role):
      mapping = {
          'Ingest Date':
          history.pop('ingestDate', None),
          'ID':
          history.pop('uniqueEmployeeId', None),
          'Name':
          map_employee_name(history),
          'Preferred Name':
          history.pop('preferredName', None),
          'ONS ID':
          history.pop('onsId', None),
          'Personal Mobile Number':
          history.pop('telephoneNumberContact1', None),
          'Home Phone Number':
          history.pop('telephoneNumberContact2', None),
          'Status':
          history.pop('status', None),
          'Badge ID':
          history.pop('idBadgeNo', None),
          'Personal Email Address':
          history.pop('personalEmailAddress', None),
          'Postcode':
          history.pop('postcode', None),
          'Country':
          history.pop('country', None),
          'Emergency Contact Name':
          history.pop('emergencyContactFullName', None),
          'Emergency Contact Mobile Number':
          history.pop('emergencyContactMobileNo', None),
          'Weekly Hours':
          history.pop('weeklyHours', None),
          'Mobility':
          history.pop('mobility', None),
      }

      mapping_entries.append(mapping)

    elif role_matchers.hr_combined_regex.match(user_role):
      # TODO this may be a duplicate
      history['address'] = ' '.join(v for v in (history['address1'],
                                                history['address2'])
                                    if v is not None)

      mapping = {
          'Ingest Date':
          history.pop('ingestDate', None),
          'ID':
          history.pop('uniqueEmployeeId', None),
          'Name':
          map_employee_name(history),
          'Preferred Name':
          history.pop('preferredName', None),
          'ONS ID':
          history.pop('onsId', None),
          'Personal Mobile Number':
          history.pop('telephoneNumberContact1', None),
          'Status':
          history.pop('status', None),
          'Badge ID':
          history.pop('idBadgeNo', None),
          'Personal Email Address':
          history.pop('personalEmailAddress', None),
          'Address':
          history.pop('address', None),
          'County':
          history.pop('county', None),
          'Postcode':
          history.pop('postcode', None),
          'Country':
          history.pop('country', None),
          'Emergency Contact Name':
          history.pop('emergencyContactFullName', None),
          'Emergency Contact Mobile Number':
          history.pop('emergencyContactMobileNo', None),
          'Date of Birth':
          history.pop('dob', None),
          'Weekly Hours':
          history.pop('weeklyHours', None),
          'Mobility':
          history.pop('mobility', None),
      }

      mapping_entries.append(mapping)

  return table_generation(mapping_entries)


def map_employee_history_job_role_table_headers(
    employee_history_job_role_table):
  employee_history_job_role_table_mapped = []

  for job_roles in employee_history_job_role_table:
    employee_history_job_role_table_mapping = {
        'Operational Start Date':
        format_to_uk_dates(job_roles.pop('contractStartDate')),
        'Operational End Date':
        format_to_uk_dates(job_roles.pop('operationalEndDate')),
        'Job Role ID':
        job_roles.pop('uniqueRoleId'),
        'Job Role':
        job_roles.pop('jobRole'),
        'Area Location':
        job_roles.pop('areaLocation'),
        'Assignment Status':
        job_roles.pop('assignmentStatus'),
        'Active Job':
        job_roles.pop('active'),
    }

    employee_history_job_role_table_mapping[
        'Operational Start Date'] = format_to_uk_dates(
            employee_history_job_role_table_mapping['Operational Start Date'])
    employee_history_job_role_table_mapping[
        'Operational End Date'] = format_to_uk_dates(
            employee_history_job_role_table_mapping['Operational End Date'])

    if employee_history_job_role_table_mapping['Active Job']:
      employee_history_job_role_table_mapping['Active Job'] = 'Yes'
    else:
      employee_history_job_role_table_mapping['Active Job'] = 'No'

    employee_history_job_role_table_mapped.append(
        employee_history_job_role_table_mapping)

  job_role_history_table = table_generation(
      employee_history_job_role_table_mapped)

  return job_role_history_table


def map_employee_name(history):
  maybe_names = (history.get('firstName', None), history.get('surname', None))
  names = (n for n in maybe_names if n and n != '-')
  return ' '.join(names)
