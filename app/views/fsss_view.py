from app.employee_view_functions import device_details, format_line_manager
from app.tabutils import tab_generation, table_generation
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_information, current_job_role, device_information):

    employee_devices, device_number = device_details(device_information)

    line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_information)

    #To Add: Firstname, surname, prefered name
    employee_information['preferredName'] 

    #Address (to investigate which fields are inside)
    employee_information['address']


    employment_glance = {'Name': employee_name, #Gives first name or surname if either is blank
                         'ONS Email Address': employee_information['onsId'],
                         'ONS Mobile Number': device_number,
                         'Status': employee_information['status']}

    emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                    'Badge Number': employee_information['idBadgeNo'],
                    'Postcode': employee_information['postcode'],
                    'Job Role Short': current_job_role['jobRoleShort'],
                    'Job Role': current_job_role['jobRole'],
                    'Job Role Type': current_job_role['jobRoleType'],
                    'Line Manager': line_manager,
                    'Mobility': employee_information['mobility'],
                    'Mobile Staff': employee_information['mobileStaff'],
                    'Weekly Hours': employee_information['weeklyHours'],
                    'Coordinator Group': current_job_role['coordGroup'],
                    'Organisation Unit': current_job_role['uniqueRoleId']
                    }

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Status': current_job_role['crStatus'],
                  'Contract Start Date': current_job_role['contractStartDate'],
                  'Contract End Date': current_job_role['contractEndDate'],
                  'Operational Start Date': current_job_role['contractStartDate'],
                  'Operational End Date': current_job_role['operationalEndDate'],
                  'Ingest Date': employee_information['ingestDate']}

    emp_personal_details = {'Address': employee_information['address'],
                            'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                            'Home Phone Number': employee_information['telephoneNumberContact2'],
                            'Personal Email Account': employee_information['personalEmailAddress'],
                            'Emergency Contact Name': employee_information['emergencyContactFullName'],
                            'Emergency Contact Number': employee_information['emergencyContactMobileNo']
                            }

    tab_glance = tab_generation('At a Glance', employment_glance)

    tab_job_role = tab_generation('Job Role Details', emp_job_role)

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    tab_employee_device_details = table_generation(employee_devices)

    all_employee_information = {
        'all_info': tab_glance + tab_job_role + tab_employment_status + tab_employee_personal_details}

    all_employee_tabs = [all_employee_information, tab_employee_device_details]

    return all_employee_tabs
