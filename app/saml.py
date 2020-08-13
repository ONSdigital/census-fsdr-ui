# All scripting related to the Single Sign On System
# This requires four main adjustments:
#  During the initial start-up, fetch_settings must be called to initialize saml settings
# Uses configuration variables: SECRET_KEY and SAML_PATH
# Relies on a folder in the root of the project, named saml:
#  It should contain a settings.json file in accordance with OneLogin's spec
#  It should contain and idp file with the Identity Provider's XML metadata
#  It should contain required certificate files in a certs folder


import aiohttp_jinja2
from aiohttp.client_exceptions import (ClientResponseError)
from aiohttp.web import HTTPFound, RouteTableDef
from aiohttp_session import get_session
from structlog import get_logger

import os
import json
from urllib.parse import urlparse

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser


saml_routes = RouteTableDef()
logger = get_logger('fsdr-ui')


def fetch_settings(app):
    json_filename = app['SSO_CONFIG_FOLDER'] + '/settings.json'
    json_data_file = open(json_filename, 'r')
    settings_base = json.load(json_data_file)
    json_data_file.close()
    idp_filename = app['SSO_CONFIG_FOLDER'] + '/idp.xml'
    idp_data_file = open(idp_filename, 'r')
    idp_data = OneLogin_Saml2_IdPMetadataParser.parse(idp_data_file.read())
    idp_data_file.close()
    settings = OneLogin_Saml2_IdPMetadataParser.merge_settings(settings_base, idp_data)
    app['saml_settings'] = settings



def init_saml_auth(saml_req, settings):
    auth = OneLogin_Saml2_Auth(saml_req, settings)
    return auth


# Takes in an AIOHTTP request object and creates a OneLogin SAML request
def prepare_saml_req(request):
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.url.host,
        'server_port': request.url.port,
        'script_name': request.url.path,
        'get_data': request.query.copy(),
        'post_data': request.content.read(),
        'query_string': request.query_string,
    }

@saml_routes.get("/signin")
async def signin(request):
    req = prepare_saml_req(request)
    auth = init_saml_auth(req, request.app['saml_settings'])

    # if 'sso' in request.query:
    raise HTTPFound(auth.login())
        # If AuthNRequest ID need to be stored in order to later validate it, do instead
        # sso_built_url = auth.login()
        # request.session['AuthNRequestID'] = auth.get_last_request_id()
        # return redirect(sso_built_url)
    # elif 'sso2' in request.query:
        # return_to = '%sattrs/' % request.host_url
        # return redirect(auth.login(return_to))

@saml_routes.get("/logout")
async def logout(request):
    name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
    if 'samlNameId' in session:
        name_id = session['samlNameId']
    if 'samlSessionIndex' in session:
        session_index = session['samlSessionIndex']
    if 'samlNameIdFormat' in session:
        name_id_format = session['samlNameIdFormat']
    if 'samlNameIdNameQualifier' in session:
        name_id_nq = session['samlNameIdNameQualifier']
    if 'samlNameIdSPNameQualifier' in session:
        name_id_spnq = session['samlNameIdSPNameQualifier']

    return redirect(auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq))

# TODO split this section up
#@saml_routes.get("/signin")
#@saml_routes.post("/signin")
async def index(request):
    req = prepare_saml_req(request)
    auth = init_saml_auth(req, request.app['saml_settings'])
    errors = []
    error_reason = None
    not_auth_warn = False
    success_slo = False
    attributes = False
    paint_logout = False

    session = await get_session(request)

    if 'sso' in request.query:
        return redirect(auth.login())
        # If AuthNRequest ID need to be stored in order to later validate it, do instead
        # sso_built_url = auth.login()
        # request.session['AuthNRequestID'] = auth.get_last_request_id()
        # return redirect(sso_built_url)
    elif 'sso2' in request.query:
        return_to = '%sattrs/' % request.host_url
        return redirect(auth.login(return_to))
    elif 'slo' in request.query:
        name_id = session_index = name_id_format = name_id_nq = name_id_spnq = None
        if 'samlNameId' in session:
            name_id = session['samlNameId']
        if 'samlSessionIndex' in session:
            session_index = session['samlSessionIndex']
        if 'samlNameIdFormat' in session:
            name_id_format = session['samlNameIdFormat']
        if 'samlNameIdNameQualifier' in session:
            name_id_nq = session['samlNameIdNameQualifier']
        if 'samlNameIdSPNameQualifier' in session:
            name_id_spnq = session['samlNameIdSPNameQualifier']

        return redirect(auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq))
    elif 'acs' in request.query:
        request_id = None
        if 'AuthNRequestID' in session:
            request_id = session['AuthNRequestID']

        auth.process_response(request_id=request_id)
        errors = auth.get_errors()
        not_auth_warn = not auth.is_authenticated()
        if len(errors) == 0:
            if 'AuthNRequestID' in session:
                del session['AuthNRequestID']
            session['samlUserdata'] = auth.get_attributes()
            session['samlNameId'] = auth.get_nameid()
            session['samlNameIdFormat'] = auth.get_nameid_format()
            session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
            session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
            session['samlSessionIndex'] = auth.get_session_index()
            self_url = OneLogin_Saml2_Utils.get_self_url(req)
            if 'RelayState' in request.form and self_url != request.form['RelayState']:
                return redirect(auth.redirect_to(request.form['RelayState']))
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()
    elif 'sls' in request.query:
        request_id = None
        if 'LogoutRequestID' in session:
            request_id = session['LogoutRequestID']
        dscb = lambda: session.clear()
        url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
        errors = auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return redirect(url)
            else:
                success_slo = True
        elif auth.get_settings().is_debug_active():
            error_reason = auth.get_last_error_reason()

    if 'samlUserdata' in session:
        paint_logout = True
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    return render_template(
        'index.html',
        errors=errors,
        error_reason=error_reason,
        not_auth_warn=not_auth_warn,
        success_slo=success_slo,
        attributes=attributes,
        paint_logout=paint_logout
    )


@saml_routes.get("/attrs/")
def attrs():
    paint_logout = False
    attributes = False

    if 'samlUserdata' in session:
        paint_logout = True
        if len(session['samlUserdata']) > 0:
            attributes = session['samlUserdata'].items()

    return render_template('attrs.html', paint_logout=paint_logout,
                           attributes=attributes)


@saml_routes.get('/metadata/')
def metadata_handler():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp
