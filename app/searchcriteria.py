from aiohttp_session import get_session
from structlog import get_logger

logger = get_logger('fsdr-ui')

async def store_search_criteria(request, search_criteria):
    session = await get_session(request)
    if 'assignmentStatus' in search_criteria.keys():
        session['assignmentStatus'] = search_criteria.get('assignmentStatus')
    if 'jobRoleShort' in search_criteria.keys():
        session['jobRoleShort'] = search_criteria.get('jobRoleShort')
    if 'area' in search_criteria.keys():
        session['area'] = search_criteria.get('area')
    if 'surname' in search_criteria.keys():
        session['surname'] = search_criteria.get('surname')
    if 'firstName' in search_criteria.keys():
        session['firstName'] = search_criteria.get('firstName')
    if 'badgeNumber' in search_criteria.keys():
        session['badgeNumber'] = search_criteria.get('badgeNumber')
    if 'jobRoleId' in search_criteria.keys():
        session['jobRoleId'] = search_criteria.get('jobRoleId')
    if 'uniqueEmployeeId' in search_criteria.keys():
        session['uniqueEmployeeId'] = search_criteria.get('uniqueEmployeeId')

    # Added for IAT TODO remove comments and lines 
    if 'gsuite' in search_criteria.keys():
        session['gsuite'] = search_criteria.get('gsuite')
    if 'xma' in search_criteria.keys():
        session['xma'] = search_criteria.get('xma')
    if 'granby' in search_criteria.keys():
        session['granby'] = search_criteria.get('granby')
    if 'loneWorker' in search_criteria.keys():
        session['loneWorker'] = search_criteria.get('loneWorker')
    if 'serviceNow' in search_criteria.keys():
        session['serviceNow'] = search_criteria.get('serviceNow')
    

async def clear_stored_search_criteria(session):
    select_options = ["gsuite","xma","granby","loneWorker","serviceNow"]
    for key_to_clear in  select_options:
        if session.get(key_to_clear):
            del session[key_to_clear]

    if session.get('assignmentStatus'):
        del session['assignmentStatus']

    if session.get('uniqueEmployeeId'):
        del session['uniqueEmployeeId']

    if session.get('jobRoleShort'):
        del session['jobRoleShort']

    if session.get('area'):
        del session['area']

    if session.get('surname'):
        del session['surname']

    if session.get('firstName'):
        del session['firstName']

    if session.get('badgeNumber'):
        del session['badgeNumber']

    if session.get('jobRoleId'):
        del session['jobRoleId']

    if session.get('jobRoleId'):
        del session['jobRoleId']

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
