

import re
from aiohttp.web import HTTPInternalServerError
from structlog import get_logger

from app import views


logger = get_logger('fsdr-ui')


rmt_regex = re.compile('R.-....(-..(-..)?)?')
hq_fo_ccs_regex = re.compile('F.-....-..-..')
recruit_regex = re.compile('PT-FP[RP].-..-..')
hr_regex = re.compile('PT-FPH.-..-..')
fsss_regex = re.compile('(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.).-..')
logi_regex = re.compile('LT-LOG.-..-..')
cfods_regex = re.compile('DT-....-..-..')
cfots_regex = re.compile('FT-FSD.-..-..')
logi_combined_regex = re.compile('({}|{}|{})'.format(*[n for n in (logi_regex, cfods_regex, cfots_regex)]))



def invalid_role_id(role_id):
    logger.warn('Invalid role ID', role_id=role_id)
    raise HTTPInternalServerError('Invalid role ID')


def role_id_to_extract_type(role_id):
    if rmt_regex.match(role_id):
        return 'RMT'
    # HQ, FO, CCS
    elif False:
        return 'HQ'
    # Logistics
    elif logi_combined_regex.match(role_id):
        return 'LOGISTICS'
    # HR
    elif hr_regex.match(role_id):
        return 'HR'
    # FSSS
    elif fsss_regex.match(role_id):
        return 'FSSS'
    # Recruitment
    elif recruit_regex.match(role_id):
        return 'RECRUITMENT'
    # Failed to match
    else:
        invalid_role_id(role_id)


def role_id_to_view_router(role_id):
    if rmt_regex.match(role_id):
        return views.rmt_view.get_employee_tabs
    # HQ, FO, CCS
    elif False:
        return views.hq_fo_ccs_view.get_employee_tabs
    # Logistics
    elif logi_combined_regex.match(role_id):
        return views.logistics_view.get_employee_tabs
    # HR
    elif hr_regex.match(role_id):
        return views.hr_view.get_employee_tabs
    # FSSS
    elif fsss_regex.match(role_id):
        return views.fsss_view.get_employee_tabs
    # Recruitiment
    elif recruit_regex.match(role_id):
        return views.recruitment_view.get_employee_tabs
    # Failed to match
    else:
        invalid_role_id(role_id)

