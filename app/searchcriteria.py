from aiohttp_session import get_session


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

    #Added unique_employee_id search for interface action table
    if 'uniqueEmployeeId' in search_criteria.keys():
        session['uniqueEmployeeId'] = search_criteria.get('uniqueEmployeeId')



async def clear_stored_search_criteria(session):
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


def retreiveIATstatuses():

#            iat_options = [ {'value':'CREATE',      'text':'create'},
#                           {'value':'SETUP',       'text':'setup'},
#                           {'value':'UPDATE',      'text':'update'},
#                           {'value':'LEAVER',      'text':'leaver'},
#                           {'value':'LEFT',        'text':'left'},
#                           {'value':'COMPLETE',    'text':'complete'},]

    # NEXT STEP - make sure this is passed through to interfaceactiontablehandler
    # Make sure it reaches HTMl (somehow it doesnt atm!?!?!)


    add_job_roles = [{'value': 'Census area manager', 'text': 'Census area manager'}, {'value': 'Census mobile officer - 2nd intake', 'text': 'Census mobile officer - 2nd intake'}, {'value': 'Communal establishments team leader', 'text': 'Communal establishments team leader'}, {'value': 'Census coverage survey team leader', 'text': 'Census coverage survey team leader'}, {'value': 'Communal establishments officer', 'text': 'Communal establishments officer'}, {'value': 'Census coverage survey interviewer', 'text': 'Census coverage survey interviewer'}, {'value': 'Census area manager (Welsh speaking)', 'text': 'Census area manager (Welsh speaking)'}, {'value': 'Census team leader', 'text': 'Census team leader'}, {'value': 'Census engagement manager', 'text': 'Census engagement manager'}, {'value': 'Communal establishments area manager', 'text': 'Communal establishments area manager'}, {'value': 'Community adviser working with the Somali community', 'text': 'Community adviser working with the Somali community'}, {'value': 'Census Officer', 'text': 'Census Officer'}, {'value': 'Census officer - 2nd intake', 'text': 'Census officer - 2nd intake'}, {'value': 'Census coverage survey area manager', 'text': 'Census coverage survey area manager'}, {'value': 'Communal establishments team leader (Welsh speaking)', 'text': 'Communal establishments team leader (Welsh speaking)'}, {'value': 'Census officer - 1st intake', 'text': 'Census officer - 1st intake'}, {'value': 'Census mobile team leader', 'text': 'Census mobile team leader'}, {'value': 'Non-compliance field manager', 'text': 'Non-compliance field manager'}, {'value': 'Non-compliance assistant', 'text': 'Non-compliance assistant'}, {'value': 'Census officer - 3rd intake', 'text': 'Census officer - 3rd intake'}, {'value': 'Census area support', 'text': 'Census area support'}, {'value': 'Non-compliance officer', 'text': 'Non-compliance officer'}, {'value': 'Census engagement manager (Welsh speaking)', 'text': 'Census engagement manager (Welsh speaking)'}, {'value': '', 'text': 'Select a job role', 'disabled': True, 'selected': True}]

    return add_job_roles



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
