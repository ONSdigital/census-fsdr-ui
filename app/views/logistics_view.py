from app.employee_view_functions import device_details
from app.tabutils import tab_generation
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_information, current_job_role, device_information):

    employee_devices, device_number = device_details(device_information)

    employee_name = map_employee_name(employee_information)

    if employee_information['preferredName'] != '':
        preferred_name = 'None'
    else:
        preferred_name = employee_information['preferredName']

    employment_glance = {'Unique Employee ID': employee_information['uniqueEmployeeId'],
                         'Name': employee_name,
                         'Preferred Name': preferred_name,
                         'ONS Email': employee_information['onsId'],
                         'ONS Mobile Number': device_number
                         }

    emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                    'Job Role': current_job_role['jobRole'],
                    'Badge Number': employee_information['idBadgeNo'],
                    'Postcode': employee_information['postcode']
                    }

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Contract Start Date': current_job_role['contractStartDate'],
                  'Contract End Date': current_job_role['contractEndDate']
                  }

    emp_personal_details = {'Address': employee_information['address'],
                            'Country': employee_information['country'],
                            'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                            'Personal Email Account': employee_information['personalEmailAddress']
                            }

    tab_glance = tab_generation('At a Glance', employment_glance)

    tab_job_role = tab_generation('Job Role Details', emp_job_role)

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    all_employee_information = {
        'all_info': tab_glance + tab_job_role + tab_employment_status + tab_employee_personal_details}

    all_employee_tabs = [all_employee_information]

    return all_employee_tabs
