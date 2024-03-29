import re
from enum import Enum, auto

from aiohttp.web import HTTPInternalServerError
from structlog import get_logger

logger = get_logger('fsdr-ui')


# keep the following locations up to date with this Enum:
#  app.employee_view_router.role_id_to_router
class RoleEnum(Enum):
  # RMT
  RMT = auto()
  # Logistics
  LOGISTICS = auto()
  # HQ, FO, CCS, FSSS
  FSSS = auto()
  # HR, Payroll, Recruitment
  HR = auto()

  @property
  def extract_type(self):
    return self.name


rmt_regex = re.compile('R.-....(-..(-..)?)?')
non_com_regex = re.compile('FT-NCP.-Z.-..')  # Non-Compliance in HQ
self_help_regex = re.compile('LT-SHL.-..-..')  # Self-Help
msg_service_regex = re.compile('LT-CFS.-..-..')  # messaging service
health_safety_regex = re.compile('ZT-HSA.-..-..')  # health and safety
rmt_combined_regex = re.compile('({}|{}|{}|{}|{})'.format(*[
    r.pattern for r in [
        rmt_regex, non_com_regex, self_help_regex, msg_service_regex,
        health_safety_regex
    ]
]))  # keep up to date with above

hr_regex = re.compile('PT-FPH.-..-..')  # unused, see below
payroll_regex = re.compile('PT-FPP.-..-..')  # unused, see below
recruit_regex = re.compile('PT-FPR.-..-..')  # unused, see below
hr_combined_regex = re.compile(
    'PT-FP[HPR].-..-..')  # keep up to date with above

hq_fo_ccs_regex = re.compile('F.-....-..-..')  # unused, see below
cfods_regex = re.compile('DT-....-..-..')
fsss_regex = re.compile(
    '(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.).-..')  # unused, see below
fsss_combined_regex = re.compile(
    '(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.|F.-....-.|DT-....-.).-..'
)  # keep up to date with above

logi_regex = re.compile('LT-LOG.-..-..')
cfots_regex = re.compile('FT-FSD.-..-..')

logi_combined_regex = re.compile(
    '({}|{})'.format(*[n.pattern
                       for n in (logi_regex,
                                 cfots_regex)]))  # keep up to date with above

download_permission_regex = re.compile('DT-SUP.-..-..')
cfs_gsuite_regex = re.compile('LT-CFS.-..-..')


def microservices_permissions(role_id, microservice_name):
  # Defines permissions for each table
  microservice_tables_dt_sup = [
      'gsuitetable',
      'xmatable',
      'lwstable',
      'servicenowtable',
      'updatetable',
      'requestlogtable',
      'chromebooktable',
      'missingdevicestable',
      'customsql',
  ]

  accessable_to_all = [
      'devicetable',
      'iattable',
      'index',
      'search',
  ]

  cfs_accessable = [
      'gsuitetable',
  ]

  if download_permission_regex.match(role_id):
    return True

  if microservice_name in accessable_to_all:
    return True

  if (cfs_gsuite_regex.match(role_id)) and (microservice_name
                                            in cfs_accessable):
    return True

  return False


def invalid_role_id(role_id):
  msg = 'Invalid role ID: {}'.format(role_id)
  logger.warn(msg, role_id=role_id)
  raise HTTPInternalServerError(reason=msg)


def has_download_permission(role_id, microservice_name='index'):
  authorised_downloads = [
      'iattable',
      'missingdevicestable',
  ]

  if download_permission_regex.match(role_id):
    if microservice_name in authorised_downloads:
      return True

  return False


def get_role(role_id):
  if rmt_combined_regex.match(role_id):
    # This is not an error. All RMT views should go to FSSS view.
    return RoleEnum.FSSS
  # Logistics
  elif logi_combined_regex.match(role_id):
    return RoleEnum.LOGISTICS
  # HQ, FO, CCS, FSSS
  elif fsss_combined_regex.match(role_id):
    return RoleEnum.FSSS
  # HR, Payroll, Recruitment
  elif hr_combined_regex.match(role_id):
    return RoleEnum.HR
  # Failed to match
  else:
    invalid_role_id(role_id)
