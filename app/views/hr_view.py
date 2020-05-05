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
                         'ONS Mobile Number': device_number,
                         'Status': employee_information['status']}

    emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                  'Status': current_job_role['crStatus'],
                  'Operational Start Date': current_job_role['contractStartDate'],
                  'Operational End Date': current_job_role['operationalEndDate'],
                  'Ingest Date': employee_information['ingestDate']}

    emp_personal_details = {'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                            'Personal Email Account': employee_information['personalEmailAddress']
                            }

    emp_other_personal_details = {'Current Civil Servant': employee_information['currentCivilServant'],
                                  'Previous Civil Servant': employee_information['previousCivilServant'],
                                  'Civil Service Pension Recipient':
                                      employee_information['civilServicePensionRecipient'],
                                  'Date of Birth': employee_information['dob'],
                                  'Driving Information': employee_information['drivingInformation']
                                  }

    emp_diversity_information = {'Age': employee_information['age'],
                                 'Ethnicity': employee_information['ethnicity'],
                                 'Disability': employee_information['disability'],
                                 'Nationality': employee_information['nationality'],
                                 'Gender': employee_information['gender'],
                                 'Sexual Orientation': employee_information['sexualOrientation'],
                                 'Religion': employee_information['religion']
                                 }

    tab_glance = tab_generation('At a Glance', employment_glance)

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    tab_other_employee_personal_details = tab_generation('Other Personal Details', emp_other_personal_details)

    tab_employee_diversity_information = tab_generation('Diversity Information', emp_diversity_information)

    all_employee_information = {
        'all_info': tab_glance + tab_employment_status + tab_employee_personal_details
                    + tab_other_employee_personal_details + tab_employee_diversity_information}

    all_employee_tabs = [all_employee_information]

    return all_employee_tabs
