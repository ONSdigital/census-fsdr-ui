from app.employee_view_functions import device_details, format_line_manager
from app.tabutils import tab_generation, format_to_uk_dates
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_information, current_job_role, device_information):

    employee_devices, device_number = device_details(device_information)

    line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_information)

    if employee_information['preferredName'] != '':
        preferred_name = 'None'
    else:
        preferred_name = employee_information['preferredName']

    employment_glance = {'Unique Employee ID': employee_information['uniqueEmployeeId'],
                         'Name': employee_name,
                         'Preferred Name': preferred_name,
                         'ONS Email': employee_information['onsId'],
                         'ONS Mobile Number': device_number,
                         'Status': employee_information['status']}

    if employee_information['mobileStaff']:
        mobile_staff = 'Yes'
    else:
        mobile_staff = 'No'

    emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                    'Badge Number': employee_information['idBadgeNo'],
                    'Postcode': employee_information['postcode'],
                    'Job Role Short': current_job_role['jobRoleShort'],
                    'Job Role Type': current_job_role['jobRoleType'],
                    'Line Manager': line_manager,
                    'Area Location': current_job_role['areaLocation'],
                    'Mobility': employee_information['mobility'],
                    'Mobile Staff': mobile_staff,
                    'Weekly Hours': employee_information['weeklyHours']
                    }

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Status': current_job_role['crStatus'],
                  'Contract Start Date': current_job_role['contractStartDate'],
                  'Contract End Date': current_job_role['contractEndDate']
                  }

    emp_personal_details = {'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                            'Personal Email Account': employee_information['personalEmailAddress'],
                            'Emergency Contact Name': employee_information['emergencyContactFullName'],
                            'Emergency Contact Number': employee_information['emergencyContactMobileNo'],
                            }

    employee_information['dob'] = format_to_uk_dates(employee_information['dob'])
    emp_other_personal_details = {'Date of Birth': employee_information['dob']}
    tab_other_employee_personal_details = tab_generation('Other Personal Details', emp_other_personal_details)

    tab_glance = tab_generation('At a Glance', employment_glance)

    tab_job_role = tab_generation('Job Role Details', emp_job_role)

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    all_employee_information = {
        'all_info': tab_glance + tab_job_role + tab_employment_status + tab_employee_personal_details
                    + tab_other_employee_personal_details}

    all_employee_tabs = [all_employee_information]

    return all_employee_tabs
