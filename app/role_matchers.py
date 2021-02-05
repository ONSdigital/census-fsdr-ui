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
fsss_regex = re.compile(
    '(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.).-..')  # unused, see below
fsss_combined_regex = re.compile(
    '(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.|F.-....-.).-..'
)  # keep up to date with above

logi_regex = re.compile('LT-LOG.-..-..')
cfods_regex = re.compile('DT-....-..-..')
cfots_regex = re.compile('FT-FSD.-..-..')
logi_combined_regex = re.compile(
    '({}|{}|{})'.format(*[n.pattern for n in (
        logi_regex, cfods_regex, cfots_regex)]))  # keep up to date with above


download_permission_regex =  re.compile('DT-SUP.-..-..')

def invalid_role_id(role_id):
    msg = 'Invalid role ID: {}'.format(role_id)
    logger.warn(msg, role_id=role_id)
    raise HTTPInternalServerError(reason=msg)

def download_permission(role_id):
    if download_permission_regex.match(role_id):
        return True 
    else:
        return False 

def get_role(role_id):
    if rmt_combined_regex.match(role_id):
        return RoleEnum.RMT
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

