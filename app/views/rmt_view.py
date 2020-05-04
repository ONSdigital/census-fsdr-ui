import requests
from requests.auth import HTTPBasicAuth

from app.tabutils import tab_generation, table_generation, format_to_uk_dates
from app.fieldmapping import map_emergency_contact_name, map_employee_name
from app.utils import FSDR_URL, FSDR_USER, FSDR_PASS


def get_employee_tabs(user_role, employee_information, current_job_role, job_roles, device_information):
    device_number = ''
    employee_devices = []

    for information in device_information:
        for devices in information:
            for device in devices:
                if devices[device] is None:
                    devices[device] = '-'
            if 'fieldDevicePhoneNumber' in devices:
                if devices['fieldDevicePhoneNumber'] != '-':
                    device_number = devices['fieldDevicePhoneNumber']

            employee_devices.append({
                'Device ID': devices['deviceId'],
                'Device Phone Number': devices['fieldDevicePhoneNumber'],
                'Device Type': devices['deviceType']
            })

    for emp_info in employee_information:
        if employee_information[emp_info] is None:
            if emp_info == 'mobility':
                employee_information[emp_info] = 'No'
            elif emp_info == 'mobileStaff':
                employee_information[emp_info] = 'No'
            else:
                employee_information[emp_info] = '-'

    for current_role in current_job_role:
        if current_job_role[current_role] is None:
            current_job_role[current_role] = '-'

    for role in job_roles:
        if job_roles[role] is None:
            job_roles[role] = '-'

    if current_job_role['lineManagerFirstName'] == '-' and current_job_role['lineManagerSurname'] == '-':
        line_manager = '-'
    elif current_job_role['lineManagerFirstName'] == '-':
        line_manager = current_job_role['lineManagerSurname']
    elif current_job_role['lineManagerSurname'] == '-':
        line_manager = current_job_role['lineManagerFirstName']
    else:
        line_manager = current_job_role['lineManagerFirstName'] + ' ' + current_job_role[
            'lineManagerSurname']

    employee_name = map_employee_name(employee_information)

    if user_role == 'rmt':
        if employee_information['preferredName'] == '':
            preferred_name = employee_information['preferredName']
        else:
            preferred_name = employee_information['preferredName']

        employment_glance = {'Name': employee_name,
                             'Preferred Name': preferred_name,
                             'ONS Email': employee_information['onsId'],
                             'ONS Mobile Number': device_number,
                             'Status': employee_information['status']}

        if employee_information['mobileStaff']:
            mobile_staff = 'Yes'
        else:
            mobile_staff = 'No'

        if employee_information['workRestrictions'] == '':
            work_restrictions = 'None'
        else:
            work_restrictions = employee_information['workRestrictions']

        emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                        'Badge Number': employee_information['idBadgeNo'],
                        'Postcode': employee_information['postcode'],
                        'Job Role Short': current_job_role['jobRoleShort'],
                        'Line Manager': line_manager,
                        'Area Location': current_job_role['areaLocation'],
                        'Mobility': employee_information['mobility'],
                        'Mobile Staff': mobile_staff,
                        'Weekly Hours': employee_information['weeklyHours'],
                        'Work Restrictions': work_restrictions
                        }

        emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                      'Status': current_job_role['crStatus'],
                      'Contract Start Date': current_job_role['contractStartDate'],
                      'Contract End Date': current_job_role['contractEndDate']
                      }

        if employee_information['welshLanguageSpeaker']:
            welsh_speaker = 'Yes'
        else:
            welsh_speaker = 'No'

        if employee_information['anyLanguagesSpoken'] == '':
            any_languages_spoken = 'None'
        else:
            any_languages_spoken = employee_information['anyLanguagesSpoken']

        emp_personal_details = {'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                                'Personal Email Account': employee_information['personalEmailAddress'],
                                'Welsh Speaker': welsh_speaker,
                                'Any Languages Spoken': any_languages_spoken
                                }
    else:
        employment_glance = {'Name': employee_name,
                             'ONS Email Address': employee_information['onsId'],
                             'ONS Mobile Number': device_number,
                             'Status': employee_information['status']}

    if user_role != 'hr' and user_role != 'rmt':
        emp_job_role = {'Job Role ID': current_job_role['uniqueRoleId'],
                        'Badge Number': employee_information['idBadgeNo'],
                        'Postcode': employee_information['postcode'],
                        'Job Role Short': current_job_role['jobRoleShort'],
                        'Job Role': current_job_role['jobRole'],
                        'Job Role Type': current_job_role['jobRoleType'],
                        'Line Manager': line_manager,
                        'Area Location': current_job_role['areaLocation'], 'Mobility': employee_information['mobility'],
                        'Mobile Staff': employee_information['mobileStaff'],
                        'Weekly Hours': employee_information['weeklyHours'],
                        'Coordinator Group': current_job_role['coordGroup'],
                        'Organisation Unit': current_job_role['uniqueRoleId']
                        }

    if user_role != 'rmt':
        emp_status = {'Assignment Status': current_job_role['assignmentStatus'],
                      'Status': current_job_role['crStatus'],
                      'Contract Start Date': current_job_role['contractStartDate'],
                      'Contract End Date': current_job_role['contractEndDate'],
                      'Operational Start Date': current_job_role['contractStartDate'],
                      'Operational End Date': current_job_role['operationalEndDate'],
                      'Ingest Date': employee_information['ingestDate']}

    if user_role != 'hr' and user_role != 'rmt':
        emergency_contacts = map_emergency_contact_name(employee_information)

        emergency_contact_name_1 = emergency_contacts[0]

        emergency_contact_name_2 = emergency_contacts[1]
    else:
        del emp_status['Contract Start Date']
        del emp_status['Contract End Date']

    if user_role != 'hr' and user_role != 'rmt':
        if user_role == 'recruitment':
            employee_information['address'] = employee_information['address1'] + ' ' + employee_information['address2']
            employee_information['telephoneNumberContact2'] = ''

        emp_personal_details = {'Address': employee_information['address'],
                                'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                                'Home Phone Number': employee_information['telephoneNumberContact2'],
                                'Personal Email Account': employee_information['personalEmailAddress'],
                                'Emergency Contact 1 Name': emergency_contact_name_1,
                                'Emergency Contact 1 Number': employee_information['emergencyContactMobileNo'],
                                'Emergency Contact 2 Name': emergency_contact_name_2, 'Emergency Contact 2 Number':
                                    employee_information['emergencyContactMobileNo2']
                                }

        if user_role == 'recruitment':
            del emp_personal_details['Home Phone Number']
    elif  user_role != 'rmt':
        emp_personal_details = {'Personal Mobile Number': employee_information['telephoneNumberContact1'],
                                'Personal Email Account': employee_information['personalEmailAddress']
                                }

    if user_role != 'fsss':
        employee_information['dob'] = format_to_uk_dates(employee_information['dob'])
        if user_role == 'hr':
            emp_other_personal_details = {'Current Civil Servant': employee_information['currentCivilServant'],
                                          'Previous Civil Servant': employee_information['previousCivilServant'],
                                          'Civil Service Pension Recipient':
                                              employee_information['civilServicePensionRecipient'],
                                          'Date of Birth': employee_information['dob'],
                                          'Driving Information': employee_information['drivingInformation']
                                          }
        else:
            emp_other_personal_details = {'Date of Birth': employee_information['dob']}

        if user_role != 'rmt':
            emp_diversity_information = {'Age': employee_information['age'],
                                         'Ethnicity': employee_information['ethnicity'],
                                         'Disability': employee_information['disability'],
                                         'Nationality': employee_information['nationality'],
                                         'Gender': employee_information['gender'],
                                         'Sexual Orientation': employee_information['sexualOrientation'],
                                         'Religion': employee_information['religion']
                                         }

    else:
        emp_other_personal_details = ''
        emp_diversity_information = ''

    tab_glance = tab_generation('At a Glance', employment_glance)

    if user_role != 'hr':
        tab_job_role = tab_generation('Job Role Details', emp_job_role)
    else:
        tab_job_role = ''

    tab_employment_status = tab_generation('Employment Status', emp_status)

    tab_employee_personal_details = tab_generation('Employee Personal Details', emp_personal_details)

    if user_role != 'fsss' and user_role != 'rmt':
        tab_other_employee_personal_details = tab_generation('Other Personal Details', emp_other_personal_details)

        tab_employee_diversity_information = tab_generation('Diversity Information', emp_diversity_information)
    else:
        tab_other_employee_personal_details = ''

        tab_employee_diversity_information = ''

    if user_role != 'hr':
        tab_employee_device_details = table_generation(employee_devices)
    else:
        tab_employee_device_details = []

    all_employee_information = {
        'all_info': tab_glance + tab_job_role + tab_employment_status + tab_employee_personal_details
                    + tab_other_employee_personal_details + tab_employee_diversity_information}

    all_employee_tabs = [all_employee_information, tab_employee_device_details]

    return all_employee_tabs


def get_employee_device(employee_id):
    return requests.get(FSDR_URL + f'/devices/byEmployee/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_information(user_role, employee_id):
    return requests.get(FSDR_URL + f'/fieldforce/byId/{user_role}/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))


def get_employee_history_information(user_role, employee_id):
    return requests.get(FSDR_URL + f'/fieldforce/historyById/{user_role}/{employee_id}',
                        verify=False,
                        auth=HTTPBasicAuth(FSDR_USER, FSDR_PASS))

