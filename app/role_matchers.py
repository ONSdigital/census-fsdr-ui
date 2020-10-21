import re
from aiohttp.web import HTTPInternalServerError
from structlog import get_logger

from app import views

logger = get_logger('fsdr-ui')

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
]))

payroll_regex = re.compile('PT-FPP.-..-..')  # unused, see below
recruit_regex = re.compile('PT-FPR.-..-..')  # unused, see below
recruit_combined_regex = re.compile('PT-FP[RP].-..-..')

hr_regex = re.compile('PT-FPH.-..-..')

hq_fo_ccs_regex = re.compile('F.-....-..-..')
fsss_regex = re.compile('(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.).-..')
fsss_combined_regex = re.compile(
    '(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.|F.-....-.).-..')

logi_regex = re.compile('LT-LOG.-..-..')
cfods_regex = re.compile('DT-....-..-..')
cfots_regex = re.compile('FT-FSD.-..-..')
logi_combined_regex = re.compile(
    '({}|{}|{})'.format(*[n for n in (logi_regex, cfods_regex, cfots_regex)]))


def invalid_role_id(role_id):
    logger.warn('Invalid role ID', role_id=role_id)
    raise HTTPInternalServerError('Invalid role ID')


def role_id_to_extract_type(role_id):
    if rmt_combined_regex.match(role_id):
        return 'RMT'
    # Logistics
    elif logi_combined_regex.match(role_id):
        return 'LOGISTICS'
    # HR
    elif hr_regex.match(role_id):
        return 'HR'
    # HQ, FO, CCS
    # FSSS
    elif fsss_combined_regex.match(role_id):
        return 'FSSS'
    # Recruitment
    elif recruit_combined_regex.match(role_id):
        return 'RECRUITMENT'
    # Failed to match
    else:
        invalid_role_id(role_id)


        # TODO remove views.hq_fo_ccs_view.get_employee_tabs
def role_id_to_view_router(role_id):
    if rmt_combined_regex.match(role_id):
        return views.rmt_view.get_employee_tabs
    # Logistics
    elif logi_combined_regex.match(role_id):
        return views.logistics_view.get_employee_tabs
    # HR
    elif hr_regex.match(role_id):
        return views.hr_view.get_employee_tabs
    # HQ, FO, CCS
    # FSSS
    elif fsss_combined_regex.match(role_id):
        return views.fsss_view.get_employee_tabs
    # Recruitiment
    elif recruit_combined_regex.match(role_id):
        return views.recruitment_view.get_employee_tabs
    # Failed to match
    else:
        invalid_role_id(role_id)
