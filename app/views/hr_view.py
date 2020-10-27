from app.employee_view_functions import process_device_details, format_line_manager, extract_device_phone, extract_device_chromebook
from app.tabutils import tab_generation, format_to_uk_dates
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

    employee_name = map_employee_name(employee_info)

    preferred_name = get_emp_info('preferredName', on_false='None')

    line_manager = format_line_manager(current_job_role)

    q = cwget_emp_infowcs[)B

    glance_data = {
        'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
        'Name': employee_name,
        'Preferred Name': preferred_name,
        'ONS ID': get_emp_info('onsId'),
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
    }
    tab_glance = tab_generation('At a Glance', glance_data)

    employee_data = {
        'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
        'Name': employee_name,
        'Preferred Name': preferred_name,
        'Address': get_emp_info('address'),
        'Postcode': get_emp_info('postcode'),
        'Personal Email Account': get_emp_info('personalEmailAddress'),
        'Personal Mobile Number': get_emp_info('telephoneNumberContact1'),
        # 'Home Phone Number': employee_info['telephoneNumberContact2'],
        'Emergency Contact Name': get_emp_info('emergencyContactFullName'),
        'Emergency Contact Number': get_emp_info('emergencyContactMobileNo'),
        'Mobility': get_emp_info('mobility'),
        'Mobile Staff': get_emp_info('mobileStaff'),
        # 'Job Role Type': current_job_role['jobRoleType'],
        'Job Role': current_job_role['jobRole'],
        'Job Role ID': current_job_role['uniqueRoleId'],
        'Job Role Short': current_job_role['jobRoleShort'],
        'Line Manager': line_manager,
        'Badge Number': get_emp_info('idBadgeNo'),
        'Area Location': current_job_role['areaLocation'],
        'Country': get_emp_info('country'),  # this needs to go in fsss
        'Weekly Hours': get_emp_info('weeklyHours'),
        'Contract Start Date': format_to_uk_dates(current_job_role['contractStartDate']),
        'Contract End Date': format_to_uk_dates(current_job_role['contractEndDate']),
        # 'Operational Start Date': format_to_uk_dates(current_job_role['contractStartDate']),
        # 'Operational End Date': format_to_uk_dates(current_job_role['operationalEndDate']),
        # 'Job Role Closing Report Status': current_job_role['crStatus'],
        'Assignment Status': current_job_role['assignmentStatus'],
        'Date of Birth': get_emp_info('dob'),
        'ONS ID': get_emp_info('onsId'),
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
    }
    tab_employment_status = tab_generation('Employment Status', employee_data)

    all_tabs = [{'all_info': tab_glance + tab_employment_status}]

    return all_tabs
