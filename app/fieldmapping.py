from app.tabutils import table_generation, format_to_uk_dates

from . import role_matchers

COMMON_FIELDS = {
  'Ingest Date': 'ingestDate',
  'ID': 'uniqueEmployeeId',
  'Preferred Name': 'preferredName',
  'ONS ID': 'onsId',
  'Personal Mobile Number': 'telephoneNumberContact1',
  'Status': 'status',
  'Badge ID': 'idBadgeNo',
  'Personal Email Address': 'personalEmailAddress',
  'Postcode': 'postcode',
  'Country': 'country',
  'Emergency Contact Name': 'emergencyContactFullName',
  'Emergency Contact Mobile Number': 'emergencyContactMobileNo',
  'Weekly Hours': 'weeklyHours',
  'Mobility': 'mobility',
}

FSSS_FIELDS = {
  'Home Phone Number': 'telephoneNumberContact2',
}

HR_FIELDS = {
  'County': 'county',
  'Date of Birth': 'dob',
}

JOB_ROLE_FIELDS = {
  'Job Role ID': 'uniqueRoleId',
  'Job Role': 'jobRole',
  'Area Location': 'areaLocation',
  'Assignment Status': 'assignmentStatus',
  'Active Job': 'active',
}

JOB_ROLE_DATE_FIELDS = {
  'Operation Start Date': 'contractStartDate',
  'Operation End Date': 'operationalEndDate',
}

def map_employee_history_table_headers(user_role, full_history):
    mapping_entries = []

    for history in full_history:
        if role_matchers.fsss_combined_regex.match(user_role):
            mapping = {}
            for mapField, histField in COMMON_FIELDS.items():
                mapping[mapField] = history.get(histField, None)
            for mapField, histField in FSSS_FIELDS.items():
                mapping[mapField] = history.get(histField, None)
            mapping['Name'] = map_employee_name(history)

            mapping_entries.append(mapping)

        elif role_matchers.hr_combined_regex.match(user_role):
            # TODO this may be a duplicate
            mapping = {}
            for mapField, histField in COMMON_FIELDS.items():
                mapping[mapField] = history.get(histField, None)
            for mapField, histField in HR_FIELDS.items():
                mapping[mapField] = history.get(histField, None)
            mapping['Name'] = map_employee_name(history)
            history['Address'] = ' '.join(v for v in (history['address1'], history['address2']) if v is not None)

            mapping_entries.append(mapping)

    return table_generation(mapping_entries)


def map_employee_history_job_role_table_headers(employee_history_job_role_table):
    mapping_entries = []

    for job_roles in employee_history_job_role_table:
        mapping = {}
        for mapField, jrField in JOB_ROLE_FIELDS.items():
            mapping[mapField] = job_roles.get(jrField, None)
        for mapField, jrField in JOB_ROLE_DATE_FIELDS.items():
            mapping[mapField] = format_to_uk_dates(job_roles.get(jrField, None))
        mapping['Active Job'] = 'Yes' if job_roles.get('active', None) else 'No'

        mapping_entries.append(mapping)

    return table_generation(mapping_entries)


def map_employee_name(history):
    maybe_names = (history.get('firstName', None), history.get('surname', None))
    names = (n for n in maybe_names if n and n != '-')
    return ' '.join(names)

