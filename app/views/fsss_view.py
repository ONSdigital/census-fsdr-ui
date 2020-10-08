from app.employee_view_functions import process_device_details, format_line_manager
from app.tabutils import tab_generation, table_generation
from app.fieldmapping import map_employee_name


def get_employee_tabs(employee_info, current_job_role, device_information):

    employee_devices, device_numbers = process_device_details(
        device_information)

    line_manager = format_line_manager(current_job_role)

    employee_name = map_employee_name(employee_info)

    preferred_name = employee_info['preferredName'] or 'None'

    employee_data = {
        'Unique Employee ID': employee_info['uniqueEmployeeId'],
        'Name': employee_name,
        'Preferred Name': preferred_name,
        'Address': employee_info['address'],
        'Postcode': employee_info['postcode'],
        'Personal Email Account': employee_info['personalEmailAddress'],
        'Personal Mobile Number': employee_info['telephoneNumberContact1'],
        'Home Phone Number': employee_info['telephoneNumberContact2'],
        'Emergency Contact Name': employee_info['emergencyContactFullName'],
        'Emergency Contact Number': employee_info['emergencyContactMobileNo'],
        'Mobility': employee_info['mobility'],
        'Mobile Staff': employee_info['mobileStaff'],
        'Job Role Type': current_job_role['jobRoleType'],
        'Job Role': current_job_role['jobRole'],
        'Job Role ID': current_job_role['uniqueRoleId'],
        'Job Role Short': current_job_role['jobRoleShort'],
        'Line Manager': line_manager,
        'Badge Number': employee_info['idBadgeNo'],
        'Area Location': current_job_role['areaLocation'],
        'Work Restrictions': employee_info['workRestrictions'],
        'Weekly Hours': employee_info['weeklyHours'],
        'Contract Start Date': current_job_role['contractStartDate'],
        'Contract End Date': current_job_role['contractEndDate'],
        'Operational Start Date': current_job_role['contractStartDate'],
        'Operational End Date': current_job_role['operationalEndDate'],
        'Job Role Closing Report Status': current_job_role['crStatus'],
        'Assignment Status': current_job_role['assignmentStatus'],

        # Unused fields:
        #'Status': employee_info['status'],
        #'Coordinator Group': current_job_role['coordGroup'],
        #'Organisation Unit': current_job_role['uniqueRoleId'],
        #'Ingest Date': employee_info['ingestDate'],
    }

    other_data = {
        'ONS ID': employee_info['onsId'],
        'Mobile Asset ID': device_information[0]['Device ID'],
        # Missing: chromebook asset id
        'Device Type': device_information[0]['Device Type'],
        'ONS Mobile Number': device_numbers[0] or '',
    }

    tab_employee_data = tab_generation('Employee Data', employee_data)

    tab_other_data = tab_generation('Other Data', other_data)

    all_employee_information = {'all_info': tab_employee_data + tab_other_data}

    all_employee_tabs = [
        all_employee_information, tab_employee_data, tab_other_data
    ]

    return all_employee_tabs
