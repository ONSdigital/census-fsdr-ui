from aiohttp_session import get_session
from structlog import get_logger
from .microservice_tables import get_fields

logger = get_logger('fsdr-ui')


async def store_search_criteria(request, search_criteria, fields_to_load=[]):
  session = await get_session(request)

  for atribute in fields_to_load:
    if atribute in search_criteria.keys():
      session[atribute] = search_criteria.get(atribute)


async def clear_stored_search_criteria(request, microservice_name=''):
  session = await get_session(request)

  field_classes = await get_fields(microservice_name, request)
  database_names = [field.database_name for field in field_classes]

  for key_to_clear in database_names:
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
