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
""" Class: LoginFormChallenger

$Id$
"""

from urllib import quote_plus

from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.Folder import Folder
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import ILoginPasswordHostExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

_DEFAULT_LOGIN_FIELD = '__ac_name'
_DEFAULT_PASSWORD_FIELD = '__ac_password'

manage_addLoginFormChallengerForm = PageTemplateFile(
    'www/lfcAdd', globals(), __name__='manage_addLoginFormChallengerForm')

def addLoginFormChallenger( dispatcher
                          , id
                          , title=None
                          , login_field=''
                          , password_field=''
                          , REQUEST=None
                          ):
    """ Add a LoginFormChallenger to a Pluggable Auth Service.
    """
    sp = LoginFormChallenger(id, title, login_field, password_field)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'LoginFormChallenger+added.'
                                    % dispatcher.absolute_url() )


class LoginFormChallenger(Folder, BasePlugin):
    """ Plugin for managing form-based challenges.
    """
    __implements__ = ( ILoginPasswordHostExtractionPlugin
                     , IChallengePlugin
                     )

    meta_type = 'Login Form Challenger'
    login_path = 'login_form'
    login_field = _DEFAULT_LOGIN_FIELD
    password_field = _DEFAULT_PASSWORD_FIELD
    security = ClassSecurityInfo()

    _properties = ( { 'id'    : 'title'
                    , 'label' : 'Title'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'login_path'
                    , 'label' : 'Login Form'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'login_field'
                    , 'label' : 'Login Field Name'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  , { 'id'    : 'password_field'
                    , 'label' : 'Password Field Name'
                    , 'type'  : 'string'
                    , 'mode'  : 'w'
                    }
                  )

    manage_options = ( BasePlugin.manage_options[:1]
                     + Folder.manage_options[:1]
                     + Folder.manage_options[2:]
                     )

    def __init__(self, id, title=None, login_field='', password_field=''):
        self._setId(id)
        self.title = title

        if login_field:
            self.login_field = login_field

        if password_field:
            self.password_field = password_field

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """ Extract credentials from form.
        """
        creds = {}

        # Look in the request for the names coming from the login form
        login = request.get(self.login_field, '')
        password = request.get(self.password_field, '')

        if login:
            creds['login'] = login
            creds['password'] = password

        if creds:
            creds['remote_host'] = request.get('REMOTE_HOST', '')

            try:
                creds['remote_address'] = request.getClientAddr()
            except AttributeError:
                creds['remote_address'] = request.get('REMOTE_ADDR', '')

        return creds

    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw):
        """ Challenge the user for credentials.
        """
        return self.unauthorized()

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

    security.declarePrivate('unauthorized')
    def unauthorized(self):
        req = self.REQUEST
        resp = req['RESPONSE']

        # Redirect if desired.
        url = self.getLoginURL()

        if url is None:
            # Could not challenge.
            return 0

        came_from = req.get('came_from', None)
        
        if came_from is not None:
            # If came_from contains a value it means the user
            # must be coming through here a second time
            # Reasons could be typos when providing credentials
            # or a redirect loop (see below)
            req_url = req.get('URL', '')

            if req_url and req_url == url:
                # Oops... The login_form cannot be reached by the user -
                # it might be protected itself due to misconfiguration -
                # the only sane thing to do is to give up because we are
                # in an endless redirect loop.
                return 0

        else:
            came_from = req.get('URL', '')

        query = req.get('QUERY_STRING', '')

        if query.startswith('?'):
            query = query[1:]

        terms = filter(None, query.split('&'))

        if came_from:
            terms.insert(0, 'came_from=%s' % quote_plus(came_from))

        if terms:
            url = '%s?%s' % (url, '&'.join(terms))

        resp.redirect(url, lock=1)
        return 1

    security.declarePrivate('getLoginURL')
    def getLoginURL(self):
        """ Where to send people for logging in """
        if self.login_path.startswith('/'):
            return self.login_path
        elif self.login_path != '':
            return '%s/%s' % (self.absolute_url(), self.login_path)
        else:
            return None

InitializeClass(LoginFormChallenger)


BASIC_LOGIN_FORM = """<html>
  <head>
    <title> Login Form </title>
  </head>

  <body>

    <h3> Please log in </h3>

    <form method="post" action=""
          tal:attributes="action string:${here/aq_parent/absolute_url}/login">

      <input type="hidden" name="came_from" value=""
             tal:attributes="value request/came_from | string:"/>
      <table cellpadding="2">
        <tr>
          <td><b>Login:</b> </td>
          <td><input type="text" name="__ac_name" size="30"
                     tal:attributes="name string:${here/login_field}" /></td>
        </tr>
        <tr>
          <td><b>Password:</b></td>
          <td><input type="password" name="__ac_password" size="30"
                     tal:attributes="name string:${here/password_field}" /></td>
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

