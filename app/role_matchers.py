

import re
from aiohttp.web import HTTPInternalServerError

import app.views


logger = get_logger('fsdr-ui')

rmt_regex = re.compile('R.-....-..-..')
hq_fo_ccs_regex = re.compile('F.-....-..-..')
recruit_regex = re.compile('PT-FP[RP].-..-..')
hr_regex = re.compile('PT-FPH.-..-..')
fsss_regex = re.compile('(ZT-HSA.-.|LT-CFS1-Z|DT-SUP.-.).-..')
logi_regex = re.compile('LT-LOG.-..-..')

def invalid_role_id(role_id):
    logger.warn('Invalid RoleID', client_ip=request['client_ip'])
    raise HTTPInternalServerError('Invalid role ID')


def role_id_to_extract_type(role_id):
    if rmt_regex.match(role_id):
        return 'RMT'
    # HQ, FO, CCS
    elif hq_fo_ccs_regex.match(role_id):
        return 'HQ'
    # Logistics
    elif logi_regex.match(role_id):
        return 'LOGISTICS'
    # HR
    elif hr_regex.match(role_id):
        return 'HR'
    # FSSS
    elif fsss_regex.match(role_id):
        return 'FSSS'
    # Recruitiment
    elif recruit_regex.match(role_id):
        return 'RECRUITMENT'
    # Failed to match
    else:
        invalid_role_id()


def role_id_to_view_router(role_id):
    if rmt_regex.match(role_id):
        return views.rmt_view.get_employee_tabs
    # HQ, FO, CCS
    elif hq_fo_ccs_regex.match(role_id):
        return views.hq_fo_ccs_view.get_employee_tabs
    # Logistics
    elif logi_regex.match(role_id):
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
        invalid_role_id()

