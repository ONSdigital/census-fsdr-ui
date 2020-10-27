from app.employee_view_functions import process_device_details, format_line_manager, extract_device_phone, extract_device_chromebook
from app.tabutils import tab_generation, table_generation, format_to_uk_dates
from app.fieldmapping import map_employee_name



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

    details_for_field_worker = {
        'Name': employee_name,
        'Preferred Name': preferred_name,
        # Gender refferenced here in GUI designs, but not in required excell spreadsheet, therefore ignored
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
        'ONS ID': get_emp_info('onsId'),  #This is Email address
    }

    employment_status = {
        'Assignment Status':
        current_job_role['assignmentStatus'],
        # "Status" in GUI here
        'Contract Start Date':
        format_to_uk_dates(current_job_role['contractStartDate']),
        'Contract End Date':
        format_to_uk_dates(current_job_role['contractEndDate']),
        'Operational Start Date':
        format_to_uk_dates(current_job_role['contractStartDate']),
        'Operational End Date':
        format_to_uk_dates(current_job_role['operationalEndDate']),
        # "Ingest date" in GUI here
    }

    job_role_for_field_worker = {
        'Job Role ID': current_job_role['uniqueRoleId'],
        # badge number
        'Postcode': get_emp_info('postcode'),
        'Job Role Short': current_job_role['jobRoleShort'],
        'Job Role': current_job_role['jobRole'],
        # device build
        'Line Manager': line_manager,
        # Area Location
        'Mobility': get_emp_info('mobility'),
        'Mobile Staff': get_emp_info('mobileStaff'),
        'Weekly Hours': get_emp_info('weeklyHours'),
        # Area group
        # Coordinator group
        # Organisation unit
    }

    personal_contact_details = {
        'Address': get_emp_info('address'),
        'Personal Mobile Number': get_emp_info('telephoneNumberContact1'),
        'Home Phone Number': get_emp_info('telephoneNumberContact2'),
        'Personal Email Account': get_emp_info('personalEmailAddress'),
        'Emergency Contact Name': get_emp_info('emergencyContactFullName'),
        'Emergency Contact Number': get_emp_info('emergencyContactMobileNo'),
    }

    devices_for_field_worker = {
        'Mobile Asset ID': (phone and phone['Device ID']) or None,
        # Device phone number
        'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
        # Device Type
    }

    other_data = {
        'Job Role Type': current_job_role['jobRoleType'],
        'Badge Number': get_emp_info('idBadgeNo'),
        'Job Role Closing Report Status': current_job_role['crStatus'],

        # Unused fields:
        #'Status': get_emp_info('status'),
        #'Coordinator Group': current_job_role['coordGroup'],
        #'Organisation Unit': current_job_role['uniqueRoleId'],
        #'Ingest Date': get_emp_info('ingestDate'),
        'Chromebook Asset ID': (chr_book and chr_book['Device ID']) or None,
        # 'Device Type': device_information[0]['Device Type'], # This doesn't make any sense
    }

    tab_details_for_field_worker = tab_generation('Details for Field Worker',
                                                  details_for_field_worker)

    tab_employment_status = tab_generation('Employment Status',
                                           employment_status)

    tab_job_role_for_field_worker = tab_generation('Job Role for Field Worker',
                                                   job_role_for_field_worker)

    tab_personal_contact_details = tab_generation('Personal Contact Details',
                                                  personal_contact_details)

    tab_devices_for_field_worker = tab_generation('Devices for Field Worker',
                                                  devices_for_field_worker)

    tab_other_data = tab_generation('Other Data', other_data)

    all_employee_information = {
        'all_info':
        tab_employment_status + tab_details_for_field_worker +
        tab_job_role_for_field_worker + tab_personal_contact_details +
        tab_devices_for_field_worker + tab_other_data
    }

    all_employee_tabs = [
        tab_details_for_field_worker, tab_employment_status,
        tab_job_role_for_field_worker, tab_personal_contact_details,
        tab_devices_for_field_worker, tab_other_data
    ]

    return all_employee_tabs
