from aiohttp_session import get_session
from structlog import get_logger
from .microservice_tables import get_fields

logger = get_logger('fsdr-ui')


async def store_search_criteria(request, search_criteria, fields_to_load=[]):
  session = await get_session(request)
  possible_stored_atributes = [
      'assignmentStatus',
      'jobRoleShort',
      'area',
      'surname',
      'firstName',
      'badgeNumber',
      'jobRoleId',
      'uniqueEmployeeId',
      'gsuite',
      'xma',
      'granby',
      'loneWorker',
      'serviceNow',
      'device_sent_options',
      'device_id',
      'field_device_phone_number',
      'device_type',
      'distinct_job_roles',
      'ons_id',
      'device_sent',
      'employee_id',
      'user_missing_device',
      'unique_employee_id',
      'setup',
      'job_role_short',
  ]

  possible_stored_atributes = possible_stored_atributes + fields_to_load

  for atribute in possible_stored_atributes:
    if atribute in search_criteria.keys():
      session[atribute] = search_criteria.get(atribute)


async def clear_stored_search_criteria(session, microservice_name=''):
  possible_stored_atributes = [
      'assignmentStatus',
      'jobRoleShort',
      'area',
      'surname',
      'job_role_short',
      'job_role_select',
      'firstName',
      'badgeNumber',
      'jobRoleId',
      'uniqueEmployeeId',
      'gsuite',
      'xma',
      'granby',
      'loneWorker',
      'serviceNow',
      'device_sent_options',
      'device_id',
      'field_device_phone_number',
      'device_type',
      'distinct_job_roles',
      'ons_id',
      'device_sent',
      'employee_id',
      'user_missing_device',
      'unique_employee_id',
      'setup',
  ]

  if microservice_name != '':
    field_classes = await get_fields(microservice_name)
    database_names = [field.database_name for field in field_classes]
    possible_stored_atributes = possible_stored_atributes + database_names

  for key_to_clear in possible_stored_atributes:
    if session.get(key_to_clear):
      del session[key_to_clear]


def load_search_criteria(data, fields_to_load):
  # "data"can be session if it's called from page 2
  search_criteria = {}
  previous_criteria = {}

  for field in fields_to_load:
    if data.get(field):
      if (data.get(field) != "blank") and (data.get(field) != "None"):
        search_criteria[field] = data.get(field)
        previous_criteria[field] = data.get(field)
      else:
        previous_criteria[field] = ''
    else:
      previous_criteria[field] = ''

  return search_criteria, previous_criteria


def retrieve_job_roles(job_roles, previous_jobrole_selected):
  add_job_roles = []
  job_shorts = job_roles.json()
  for job_role_short in job_shorts:
    if job_role_short is None:
      continue
    elif job_role_short == previous_jobrole_selected:
      add_job_roles.append(
          {
              'value': job_role_short,
              'text': job_role_short,
              "disabled": False,
              "selected": True
          }, )
    else:
      add_job_roles.append({'value': job_role_short, 'text': job_role_short}, )

  if not previous_jobrole_selected:
    add_job_roles.append({
        "value": "",
        "text": "Select a job role",
        "disabled": True,
        "selected": True
    })

  return add_job_roles


def retrieve_assignment_statuses(assignment_statuses):
  add_assignment = []
  for assignments in assignment_statuses.json():
    add_assignment.append({'value': assignments, 'text': assignments}, )
  add_assignment.append({
      "value": "",
      "text": "Select assignment status",
      "disabled": True,
      "selected": True
  })

  return add_assignment
