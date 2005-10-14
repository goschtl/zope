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
""" Class: CookieAuthHelper

$Id$
"""

from base64 import encodestring, decodestring
from urllib import quote, unquote

from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.Folder import Folder
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import ILoginPasswordHostExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins \
        import ICredentialsInitializePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import ICredentialsUpdatePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import ICredentialsResetPlugin


manage_addCookieAuthHelperForm = PageTemplateFile(
    'www/caAdd', globals(), __name__='manage_addCookieAuthHelperForm')


_DEFAULT_COOKIE_NAME = '__ginger_snap'

def addCookieAuthHelper( dispatcher
                       , id
                       , title=None
                       , cookie_name=_DEFAULT_COOKIE_NAME
                       , REQUEST=None
                       ):
    """ Add a Cookie Auth Helper to a Pluggable Auth Service. """
    sp = CookieAuthHelper(id, title, cookie_name)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'CookieAuthHelper+added.'
                                    % dispatcher.absolute_url() )


class CookieAuthHelper(Folder, BasePlugin):
    """ Multi-plugin for managing details of Cookie Authentication. """
    __implements__ = ( ILoginPasswordHostExtractionPlugin
                     , ICredentialsInitializePlugin
                     , ICredentialsUpdatePlugin
                     , ICredentialsResetPlugin
                     )

    meta_type = 'Cookie Auth Helper'
    cookie_name = _DEFAULT_COOKIE_NAME
    login_path = 'login_form'
    security = ClassSecurityInfo()

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'cookie_name'
                    , 'label' : 'Cookie Name'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'login_path'
                    , 'label' : 'Login Form'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  )

    manage_options = ( BasePlugin.manage_options[:1]
                     + Folder.manage_options[:1]
                     + Folder.manage_options[2:]
                     )

    def __init__(self, id, title=None, cookie_name=''):
        self._setId(id)
        self.title = title

        if cookie_name:
            self.cookie_name = cookie_name


    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Extract credentials from cookie or 'request'.
        """
        credentials = {}
        cookie = request.get(self.cookie_name, '')

        if cookie:
            cookie_val = decodestring(unquote(cookie))
            login, password = cookie_val.split(':')

            credentials['login'] = login
            credentials['password'] = password

        if credentials:
            credentials['remote_host'] = request.get('REMOTE_HOST', '')

            try:
                credentials['remote_address'] = request.getClientAddr()
            except AttributeError:
                credentials['remote_address'] = request.get('REMOTE_ADDR', '')

        return credentials


    security.declarePrivate('initializeCredentials')
    def initializeCredentials(self, request, response, credentials):
        """ Notification that newly-authenticated credentials exist.
        """
        if response.cookies.get(self.cookie_name) is not None:
            return

        login = credentials.get( 'login', '')
        password = credentials.get( 'password', '')

        if login and password:

            cookie_val = encodestring('%s:%s' % (login, password))
            cookie_val = cookie_val.rstrip()
            response.setCookie(self.cookie_name, quote(cookie_val), path='/')

    security.declarePrivate('updateCredentials')
    def updateCredentials(self, request, response, credentials):
        """ Notification that user has changed credentials.
        """
        login = credentials.get( 'login', '')
        password = credentials.get( 'password', '')

        if login and password:

            cookie_val = encodestring('%s:%s' % (login, new_password))
            cookie_val = cookie_val.rstrip()
            response.setCookie(self.cookie_name, quote(cookie_val), path='/')

        else:
            response.expireCookie(self.cookie_name, path='/')


    security.declarePrivate('resetCredentials')
    def resetCredentials(self, request, response):
        """ Raise unauthorized to tell browser to clear credentials.
        """
        response.expireCookie(self.cookie_name, path='/')


    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ Setup tasks upon instantiation.
        """
        login_form = ZopePageTemplate( id='login_form'
                                     , text=BASIC_LOGIN_FORM
                                     )
        login_form.title = 'Login Form'
        login_form.__roles__ = []
        self._setObject( 'login_form', login_form, set_owner=0 )


InitializeClass(CookieAuthHelper)


BASIC_LOGIN_FORM = """<html>
  <head>
    <title> Login Form </title>
  </head>

  <body>

    <h3> Please log in </h3>

    <form method="post" action=""
          tal:attributes="action string:${here/absolute_url}/login">

      <input type="hidden" name="came_from" value=""
             tal:attributes="value request/came_from | string:"/>
      <table cellpadding="2">
        <tr>
          <td><b>Login:</b> </td>
          <td><input type="text" name="__ac_name" size="30" /></td>
        </tr>
        <tr>
          <td><b>Password:</b></td>
          <td><input type="password" name="__ac_password" size="30" /></td>
        </tr>
        <tr>
          <td colspan="2">
            <br />
            <input type="submit" value=" Log In " />
          </td>
        </tr>
      </table>

    </form>

  </body>

</html>
"""

