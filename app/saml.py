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
from aiohttp.web import Response, HTTPFound, RouteTableDef
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


# Build the OneLogin SAML settings structure
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


# 
def init_saml_auth(saml_req, settings):
    auth = OneLogin_Saml2_Auth(saml_req, settings)
    return auth


# Takes in an AIOHTTP request object and creates a OneLogin SAML request
async def prepare_saml_req(request):
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.url.host,
        'server_port': request.url.port,
        'script_name': request.url.path,
        'get_data': request.query.copy(),
        'post_data': await request.post(),
        'query_string': request.query_string,
    }


# Single Sign-on Service
@saml_routes.get("/signin")
async def sso(request):
    auth = init_saml_auth(await prepare_saml_req(request), request.app['saml_settings'])

    # If AuthNRequest ID need to be stored in order to later validate it, do instead:
    # sso_built_url = auth.login()
    # request.session['AuthNRequestID'] = auth.get_last_request_id()
    # return HTTPFound(sso_built_url)

    # If we need to redirect to a specific URL:
    # return_to = '%sattrs/' % request.host_url
    # return HTTPFound(auth.login(return_to))

    raise HTTPFound(auth.login())


# Assertion Consumer Service
@saml_routes.post("/signin")
async def acs(request):
    session = await get_session(request)
    post = await request.post()
    auth = init_saml_auth(await prepare_saml_req(request), request.app['saml_settings'])

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
        session['samlNameIdFormat'] = auth.get_nameid_format()
        session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
        session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
        session['samlSessionIndex'] = auth.get_session_index()
        self_url = OneLogin_Saml2_Utils.get_self_url(req)
        if 'RelayState' in post and self_url != post['RelayState']:
            return redirect(auth.redirect_to(post['RelayState']))
    elif auth.get_settings().is_debug_active():
        raise HTTPInternalServerError(text=auth.get_last_error_reason())


# Start Logout
@saml_routes.get("/logout")
async def slo(request):
    auth = init_saml_auth(await prepare_saml_req(request), request.app['saml_settings'])
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

    raise HTTPFound(auth.logout(name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq))


# Single Logout
@saml_routes.get("/logoutfull")
async def sls(request):
    session = await get_session(request)
    auth = init_saml_auth(await prepare_saml_req(request), request.app['saml_settings'])

    request_id = None
    if 'LogoutRequestID' in session:
        request_id = session['LogoutRequestID']

    dscb = lambda: session.invalidate()
    url = auth.process_slo(request_id=request_id, delete_session_cb=dscb)
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            return redirect(url)
        else:
            # TODO better return from this method
            return Response()
    elif auth.get_settings().is_debug_active():
        raise HTTPInternalServerError(text=auth.get_last_error_reason())


# Debug function for viewing attributes
@saml_routes.get("/attrs")
async def attrs(request):
    session = await get_session(request)
    if 'samlUserdata' in session:
        attributes = session['samlUserdata'].items()
        return Response(text='Attributes: ' + ', '.join(attributes), content_type='text/xml')
    else:
        raise HTTPForbidden(text='Not logged in')


# Metadata display function
@saml_routes.get('/metadata')
async def metadata(request):
    auth = init_saml_auth(await prepare_saml_req(request), request.app['saml_settings'])
    settings = auth.get_settings()
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)

    if len(errors) == 0:
        return Response(text=metadata, content_type='text/xml')
    else:
        raise HTTPInternalServerError(text=', '.join(errors))
