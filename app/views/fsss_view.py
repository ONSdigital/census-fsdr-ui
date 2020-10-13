from app.employee_view_functions import process_device_details, format_line_manager
from app.tabutils import tab_generation, table_generation
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_info, current_job_role, device_information):

    devices, device_numbers = process_device_details(device_information)
    phone = extract_device_phone(devices)
    chr_book = extract_device_chromebook(devices)

    line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_info)

    preferred_name = employee_info['preferredName'] or 'None'

    details_for_field_worker = {
        'Name': employee_name,
        'Preferred Name': preferred_name,
        # Gender refferenced here in GUI designs, but not in required excell spreadsheet, therefore ignored
        'ONS Mobile Number': (phone and phone['Device Phone Number']) or '',
        # ONS email address refferenced in GUI 
    }

    employment_status = {
        'Assignment Status': current_job_role['assignmentStatus'],
        # "Status" in GUI here
        'Contract Start Date': current_job_role['contractStartDate'],
        'Contract End Date': current_job_role['contractEndDate'],
        'Operational Start Date': current_job_role['contractStartDate'],
        'Operational End Date': current_job_role['operationalEndDate'],
        # "Ingest date" in GUI here
    }

    job_role_for_field_worker = {
        'Job Role ID': current_job_role['uniqueRoleId'],
        # badge number
        'Postcode': employee_info['postcode'],
        'Job Role Short': current_job_role['jobRoleShort'],
        'Job Role': current_job_role['jobRole'],
        # device build
        'Line Manager': line_manager,
        # Area Location
        'Mobility': employee_info['mobility'],
        'Mobile Staff': employee_info['mobileStaff'],
        'Weekly Hours': employee_info['weeklyHours'],
        # Area group
        # Coordinator group
        # Organisation unit
    }

    personal_contact_details = {
        'Address': employee_info['address'],
        'Personal Mobile Number': employee_info['telephoneNumberContact1'],
        'Home Phone Number': employee_info['telephoneNumberContact2'],
        'Personal Email Account': employee_info['personalEmailAddress'],
        'Emergency Contact Name': employee_info['emergencyContactFullName'],
        'Emergency Contact Number': employee_info['emergencyContactMobileNo'],
        # Emergency Contact Name 2
        # Emergency Contact Number 2
    }

    devices_for_field_worker = {

        'Mobile Asset ID': (phone and phone['Device ID']) or None,
        # Device phone number
        'Unique Employee ID': employee_info['uniqueEmployeeId'],
        # Device Type
    }


    other_data = {
        'Job Role Type': current_job_role['jobRoleType'],
        'Badge Number': employee_info['idBadgeNo'],
        'Work Restrictions': employee_info['workRestrictions'],
        'Job Role Closing Report Status': current_job_role['crStatus'],

        # Unused fields:
        #'Status': employee_info['status'],
        #'Coordinator Group': current_job_role['coordGroup'],
        #'Organisation Unit': current_job_role['uniqueRoleId'],
        #'Ingest Date': employee_info['ingestDate'],

        'ONS ID': employee_info['onsId'],
        'Chromebook Asset ID': (chr_book and chr_book['Device ID']) or None,
        # 'Device Type': device_information[0]['Device Type'], # This doesn't make any sense
    }

    tab_details_for_field_worker = tab_generation('Details for Field Worker', details_for_field_worker)

    tab_employment_status = tab_generation('Employment Status', employment_status)
    
    tab_job_role_for_field_worker = tab_generation('Job Role for Field Worker', job_role_for_field_worker)

    tab_personal_contact_details = tab_generation('Personal Contact Details', personal_contact_details)

    tab_devices_for_field_worker = tab_generation('Devices for Field Worker', devices_for_field_worker)

    tab_other_data = tab_generation('Other Data', other_data)

    all_employee_information =  {'all_info':  tab_employment_status + tab_details_for_field_worker + tab_job_role_for_field_worker + tab_personal_contact_details + tab_devices_for_field_worker + tab_other_data } 

    all_employee_tabs = [
        tab_details_for_field_worker, tab_employment_status, tab_job_role_for_field_worker, tab_personal_contact_details, tab_devices_for_field_worker, tab_other_data 
    ]

    return all_employee_tabs
