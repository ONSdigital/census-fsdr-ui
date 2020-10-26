from app.employee_view_functions import process_device_details, format_line_manager, extract_device_phone, extract_device_chromebook
from app.tabutils import tab_generation, format_to_uk_dates
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_info, current_job_role, device_information):

    devices, device_numbers = process_device_details(device_information)
    phone = extract_device_phone(devices)
    chr_book = extract_device_chromebook(devices)

    employee_name = map_employee_name(employee_information)

    preferred_name = employee_info['preferredName'] or 'None'

    line_manager = format_line_manager(current_job_role)

    glance_data = {
        'Unique Employee ID': employee_info['uniqueEmployeeId'],
        'Name': employee_name,
        'Preferred Name': preferred_name,
        'ONS ID': employee_info['onsId'],
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
    }
    tab_glance = tab_generation('At a Glance', glance_data)

    employee_data = {
        'Unique Employee ID': employee_info['uniqueEmployeeId'],
        'Name': employee_name,
        'Preferred Name': preferred_name,
        'Address': employee_info['address'],
        'Postcode': employee_info['postcode'],
        'Personal Email Account': employee_info['personalEmailAddress'],
        'Personal Mobile Number': employee_info['telephoneNumberContact1'],
        # 'Home Phone Number': employee_info['telephoneNumberContact2'],
        'Emergency Contact Name': employee_info['emergencyContactFullName'],
        'Emergency Contact Number': employee_info['emergencyContactMobileNo'],
        'Mobility': employee_info['mobility'],
        'Mobile Staff': employee_info['mobileStaff'],
        # 'Job Role Type': current_job_role['jobRoleType'],
        'Job Role': current_job_role['jobRole'],
        'Job Role ID': current_job_role['uniqueRoleId'],
        'Job Role Short': current_job_role['jobRoleShort'],
        'Line Manager': line_manager,
        'Badge Number': employee_info['idBadgeNo'],
        'Area Location': current_job_role['areaLocation'],
        'Country': employee_information['country'], # this needs to go in fsss
        'Weekly Hours': employee_info['weeklyHours'],
        'Contract Start Date': format_to_uk_dates(current_job_role['contractStartDate']),
        'Contract End Date': format_to_uk_dates(current_job_role['contractEndDate']),
        # 'Operational Start Date': format_to_uk_dates(current_job_role['contractStartDate']),
        # 'Operational End Date': format_to_uk_dates(current_job_role['operationalEndDate']),
        # 'Job Role Closing Report Status': current_job_role['crStatus'],
        'Assignment Status': current_job_role['assignmentStatus'],
        'Date of Birth': employee_information['dob'],
        'ONS ID': employee_info['onsId'],
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
    }
    tab_employment_status = tab_generation('Employment Status', employee_data)

    all_tabs = [{'all_info': tab_glance + tab_employment_status}]

    return all_tabs
