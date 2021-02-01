from aiohttp_session import get_session
from structlog import get_logger

logger = get_logger('fsdr-ui')

async def store_search_criteria(request, search_criteria):
    session = await get_session(request)
    possible_stored_atributes =['assignmentStatus', 'jobRoleShort','area','surname','firstName','badgeNumber',
            'jobRoleId','uniqueEmployeeId','gsuite','xma','granby','loneWorker','serviceNow',
            'device_sent_options', 'device_id','field_device_phone_number',
            'device_type','distinct_job_roles','ons_id','device_sent',
            'employee_id']

    for atribute in possible_stored_atributes:
        if atribute in search_criteria.keys():
            session[atribute] = search_criteria.get(atribute)

async def clear_stored_search_criteria(session):
    possible_stored_atributes =['assignmentStatus', 'jobRoleShort','area','surname','firstName','badgeNumber',
            'jobRoleId','uniqueEmployeeId','gsuite','xma','granby','loneWorker','serviceNow',
            'device_sent_options', 'device_id','field_device_phone_number',
            'device_type','distinct_job_roles','ons_id','device_sent',
            'employee_id']

    for key_to_clear in  possible_stored_atributes:
        if session.get(key_to_clear):
            del session[key_to_clear]


def retrieve_job_roles(job_roles, previous_jobrole_selected):
    add_job_roles = []
    job_shorts = job_roles.json()
    for job_role_short in job_shorts:
        if job_role_short is None:
            continue
        elif job_role_short == previous_jobrole_selected:
            add_job_roles.append({
                'value': job_role_short,
                'text': job_role_short,
                "disabled": False,
                "selected": True
            }, )
        else:
            add_job_roles.append({
                'value': job_role_short,
                'text': job_role_short
            }, )

    if not previous_jobrole_selected:
        add_job_roles.append({
            "value": "",
            "text": "Select a job role",
            "disabled": True,
            "selected": True
        })

    return add_job_roles

    
def set_status(dropdown_value):

# Set the default options
    dropdown_options =  [   {'value':'blank',       'text':'Select a status', "disabled": True},
                            {'value':'CREATE',      'text':'CREATE'},
                            {'value':'SETUP',       'text':'SETUP'},
                            {'value':'UPDATE',      'text':'UPDATE'},
                            {'value':'LEAVER',      'text':'LEAVER'},
                            {'value':'LEFT',        'text':'LEFT'},
                            {'value':'COMPLETE',    'text':'COMPLETE'},]

    for each_dict in dropdown_options:
        if each_dict['value'] == dropdown_value:
            each_dict['selected'] = True
             
    return dropdown_options

def device_type_dropdown(dropdown_value):
    if dropdown_value == '':
        dropdown_value = "blank"
    dropdown_options =  [   {'value':'blank',       'text':'Select a value', "disabled": True},
                            {'value':'CHROMEBOOK',      'text':'CHROMEBOOK'},
                            {'value':'PHONE',    'text':'PHONE'},]

    for each_dict in dropdown_options:
        if each_dict['value'] == dropdown_value:
            each_dict['selected'] = True
             
    return dropdown_options

def device_sent_dropdown(dropdown_value):
    if dropdown_value == '':
        dropdown_value = "blank"
    dropdown_options =  [   {'value':'blank',       'text':'Select a value', "disabled": True},
                            {'value':'True',      'text':'True'},
                            {'value':'False',    'text':'False'},]

    for each_dict in dropdown_options:
        if each_dict['value'] == dropdown_value:
            each_dict['selected'] = True
             
    return dropdown_options


def retreive_iat_statuses(data,select_options):
    all_options = {}

    for dropdown_name in select_options:
        # if the dropdown should be a pre-selected value
        if data.get(dropdown_name):
            dropdown_value = data.get(dropdown_name)
            all_options[dropdown_name] = set_status(dropdown_value)
        else:
            all_options[dropdown_name] = set_status('blank')
        
    return all_options


def retrieve_assignment_statuses(assignment_statuses):
    add_assignment = []
    for assignments in assignment_statuses.json():
        add_assignment.append({
            'value': assignments,
            'text': assignments
        }, )
    add_assignment.append({
        "value": "",
        "text": "Select assignment status",
        "disabled": True,
        "selected": True
    })

    return add_assignment
