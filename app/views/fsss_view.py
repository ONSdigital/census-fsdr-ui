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

    data_detail = {
        'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
        'Name': employee_name,
        'Preferred Name': preferred_name,   # Asked to be added in FWMT-2681 but already present
        # Gender refferenced here in GUI designs, but not in required excell spreadsheet, therefore ignored
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
        'ONS ID': get_emp_info('onsId'),  #This is Email address
    }
    tab_detail = tab_generation('Details for Field Worker', data_detail)

    data_employment = {
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
    tab_employment = tab_generation('Employment Status', data_employment)

    data_job_role = {
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
    tab_job_role = tab_generation('Job Role for Field Worker', data_job_role)

    data_contact = {
        'Address': get_emp_info('address'),
        'Personal Mobile Number': get_emp_info('telephoneNumberContact1'),
        'Home Phone Number': get_emp_info('telephoneNumberContact2'),
        'Personal Email Account': get_emp_info('personalEmailAddress'),
        'Emergency Contact Name': get_emp_info('emergencyContactFullName'),
        'Emergency Contact Number': get_emp_info('emergencyContactMobileNo'),
    }
    tab_contact = tab_generation('Personal Contact Details', data_contact)

    data_devices = {
        'Mobile Asset ID': (phone and phone['Device ID']) or None,
        # Device phone number
        'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
        # Device Type
    }
    tab_devices = tab_generation('Devices for Field Worker', data_devices)

    data_other = {
        'Job Role Type': current_job_role['jobRoleType'],
        #'Badge Number': get_emp_info('idBadgeNo'),
        'Job Role Closing Report Status': current_job_role['crStatus'],

        # Unused fields:
        #'Status': get_emp_info('status'),
        #'Coordinator Group': current_job_role['coordGroup'],
        #'Organisation Unit': current_job_role['uniqueRoleId'],
        #'Ingest Date': get_emp_info('ingestDate'),
        'Chromebook Asset ID': (chr_book and chr_book['Device ID']) or None,
        # 'Device Type': device_information[0]['Device Type'], # This doesn't make any sense
    }
    tab_other = tab_generation('Other Data', data_other)

    tabs_all = [{
        'all_info': tab_detail + tab_employment + tab_job_role + tab_contact + tab_devices + tab_other
    }]
    return tabs_all
