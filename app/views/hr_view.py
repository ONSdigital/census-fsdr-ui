from app.employee_view_functions import process_device_details
from app.tabutils import tab_generation
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_information, current_job_role, device_information):

    devices, device_numbers = process_device_details(device_information)
    phone = extract_device_phone(devices)
    chr_book = extract_device_chromebook(devices)

    # line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_info)

    preferred_name = employee_info['preferredName'] or 'None'

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
        'Work Restrictions': employee_info['workRestrictions'],
        'Weekly Hours': employee_info['weeklyHours'],
        'Contract Start Date': current_job_role['contractStartDate'],
        'Contract End Date': current_job_role['contractEndDate'],
        # 'Operational Start Date': current_job_role['contractStartDate'],
        # 'Operational End Date': current_job_role['operationalEndDate'],
        # 'Job Role Closing Report Status': current_job_role['crStatus'],
        'Assignment Status': current_job_role['assignmentStatus'],
        'Date of Birth': employee_information['dob'],
        'ONS ID': employee_info['onsId'],
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
    }
    tab_employment_status = tab_generation('Employment Status', employee_data)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    tab_other_employee_personal_details = tab_generation('Other Personal Details', emp_other_personal_details)

    tab_employee_diversity_information = tab_generation('Diversity Information', emp_diversity_information)

    all_tabs = [{
        'all_info': tab_glance + tab_employment_status + tab_employee_personal_details
        + tab_other_employee_personal_details + tab_employee_diversity_information}]

    return all_tabs

    # old code below

    employment_glance = {'Unique Employee ID': employee_information['uniqueEmployeeId'],
                         'Name': employee_name,
                         'Preferred Name': preferred_name,
                         'ONS Email': employee_information['onsId'],
                         'ONS Mobile Number':device_numbers[0] or '' ,
                         'Status': employee_information['status'],
    }

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Status': current_job_role['crStatus'],
                  'Operational Start Date': current_job_role['contractStartDate'],
                  'Operational End Date': current_job_role['operationalEndDate'],
                  'Ingest Date': employee_information['ingestDate']}

    emp_personal_details = {'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                            'Personal Email Account': employee_information['personalEmailAddress']
                            }

    emp_other_personal_details = {'Date of Birth': employee_information['dob']}

    emp_diversity_information = {}

    return all_employee_tabs
