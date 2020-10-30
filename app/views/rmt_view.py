from app.employee_view_functions import process_device_details, format_line_manager
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


    employee_devices, device_numbers = process_device_details(device_information)

    line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_info)

    preferred_name = get_emp_info('preferredName', on_false='None')

    employment_glance = {
         'Unique Employee ID': get_emp_info('uniqueEmployeeId'),
         'Name': employee_name,
         'Preferred Name': preferred_name,
         'ONS Email': get_emp_info('onsId'),
         'ONS Mobile Number': device_numbers[0] or '',
         'Status': get_emp_info('status'),
     }

    is_mobile_staff = str(current_job_role['uniqueRoleId'])[3:6] == 'MOB'
    mobile_staff = 'Yes' if is_mobile_staff else 'No'

    emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                    'Badge Number': get_emp_info('idBadgeNo'),
                    'Postcode': get_emp_info('postcode'),
                    'Job Role Short': current_job_role['jobRoleShort'],
                    'Job Role Type': current_job_role['jobRoleType'],
                    'Line Manager': line_manager,
                    'Area Location': current_job_role['areaLocation'],
                    'Mobility': get_emp_info('mobility'),
                    'Mobile Staff': mobile_staff,
                    'Weekly Hours': get_emp_info('weeklyHours')
                    }

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Status': current_job_role['crStatus'],
                  'Contract Start Date': format_to_uk_dates(current_job_role['contractStartDate']),
                  'Contract End Date': format_to_uk_dates(current_job_role['contractEndDate']),
                  }

    emp_personal_details = {'Personal Mobile Number': get_emp_info('telephoneNumberContact1'),
                            'Personal Email Account': get_emp_info('personalEmailAddress'),
                            'Emergency Contact Name': get_emp_info('emergencyContactFullName'),
                            'Emergency Contact Number': get_emp_info('emergencyContactMobileNo'),
                            }

    tab_glance = tab_generation('At a Glance', employment_glance)

    tab_job_role = tab_generation('Job Role Details', emp_job_role)

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    all_employee_information = {
        'all_info': tab_glance + tab_job_role + tab_employment_status + tab_employee_personal_details}

    all_employee_tabs = [all_employee_information]

    return all_employee_tabs
