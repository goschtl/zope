##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Class: SessionAuthHelper

$Id$
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ILoginPasswordHostExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ICredentialsInitializePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ICredentialsUpdatePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ICredentialsResetPlugin


manage_addSessionAuthHelperForm = PageTemplateFile(
    'www/saAdd', globals(), __name__='manage_addSessionAuthHelperForm')


_DEFAULT_LOGIN_KEY = '__ac_name'
_DEFAULT_PASSWORD_KEY = '__ac_password'

def manage_addSessionAuthHelper( dispatcher
                               , id
                               , title=None
                               , login_key=''
                               , password_key=''
                               , REQUEST=None
                               ):
    """ Add a Session Auth Helper to a Pluggable Auth Service.
    """
    sp = SessionAuthHelper(id, title, login_key, password_key)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'SessionAuthHelper+added.'
                                    % dispatcher.absolute_url() )


class SessionAuthHelper(BasePlugin):
    """ Multi-plugin for managing details of Session Authentication.
    """
    __implements__ = ( ILoginPasswordHostExtractionPlugin
                     , ICredentialsInitializePlugin
                     , ICredentialsUpdatePlugin
                     , ICredentialsResetPlugin
                     )

    meta_type = 'Session Auth Helper'
    security = ClassSecurityInfo()
    login_key = _DEFAULT_LOGIN_KEY
    password_key = _DEFAULT_PASSWORD_KEY

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'login_key'
                    , 'label' : 'Login Session Key'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'password_key'
                    , 'label' : 'Password Session Key'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  )


    def __init__( self, id, title=None, login_key='', password_key='' ):

        self._setId(id)
        self.title = title

        if login_key:
            self.login_key = login_key

        if password_key:
            self.password_key = password_key

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Extract credentials from session.
        """
        creds = {}

        name = request.SESSION.get(self.login_key, '')
        password = request.SESSION.get(self.password_key, '')

        if name:
            creds[ 'login' ] = name
            creds[ 'password' ] = password

        if creds:
            creds['remote_host'] = request.get('REMOTE_HOST', '')

            try:
                creds['remote_address'] = request.getClientAddr()
            except AttributeError:
                creds['remote_address'] = request.get('REMOTE_ADDR', '')

        return creds

    security.declarePrivate('initializeCredentials')
    def initializeCredentials(self, request, response, credentials ):
        """ Respond to newly-authenticated credentials.
        """
        if request.SESSION.get(self.login_key) is not None:
            return

        login = credentials.get('login', '')
        password = credentials.get('password', '')

        if login and password:

            request.SESSION.set(self.login_key, login)
            request.SESSION.set(self.password_key, password)

    security.declarePrivate('updateCredentials')
    def updateCredentials(self, request, response, credentials ):
        """ Respond to change of credentials.
        """
        login = credentials.get('login', '')
        password = credentials.get('password', '')

        if login and password:

            request.SESSION.set(self.login_key, login)
            request.SESSION.set(self.password_key, password)

        else:
            request.SESSION.set(self.login_key, '')
            request.SESSION.set(self.password_key, '')
        
    security.declarePrivate('resetCredentials')
    def resetCredentials(self, request, response):
        """ Respond to logout request or unauthorized.
        """
        request.SESSION.set(self.login_key, '')
        request.SESSION.set(self.password_key, '')

InitializeClass(SessionAuthHelper)

