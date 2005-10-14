""" Class: HTTPBasicAuthHelper

$Id$
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import \
        ILoginPasswordHostExtractionPlugin, \
        IChallengePlugin,  \
        ICredentialsResetPlugin


manage_addHTTPBasicAuthHelperForm = PageTemplateFile(
    'www/hbAdd', globals(), __name__='manage_addHTTPBasicAuthHelperForm' )


def addHTTPBasicAuthHelper( dispatcher, id, title=None, REQUEST=None ):

    """ Add a HTTP Basic Auth Helper to a Pluggable Auth Service. 
    """
    sp = HTTPBasicAuthHelper( id, title )
    dispatcher._setObject( sp.getId(), sp )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( '%s/manage_workspace'
                                      '?manage_tabs_message='
                                      'HTTPBasicAuthHelper+added.'
                                    % dispatcher.absolute_url() )


class HTTPBasicAuthHelper( BasePlugin ):

    """ Multi-plugin for managing details of HTTP Basic Authentication.
    """
    __implements__ = ( ILoginPasswordHostExtractionPlugin
                     , IChallengePlugin
                     , ICredentialsResetPlugin
                     )

    meta_type = 'HTTP Basic Auth Helper'

    security = ClassSecurityInfo()

    def __init__( self, id, title=None ):
        self._setId( id )
        self.title = title

    security.declarePrivate( 'extractCredentials' )
    def extractCredentials( self, request ):

        """ Extract basic auth credentials from 'request'.
        """
        creds = {}
        login_pw = request._authUserPW()

        if login_pw is not None:
            name, password = login_pw

            creds[ 'login' ] = name
            creds[ 'password' ] = password
            creds[ 'remote_host' ] = request.get('REMOTE_HOST', '')

            try:
                creds[ 'remote_address' ] = request.getClientAddr()
            except AttributeError:
                creds[ 'remote_address' ] = ''

        return creds

    security.declarePrivate( 'challenge' )
    def challenge( self, request, response, **kw ):

        """ Challenge the user for credentials.
        """
        # XXX:  Does this need to check whether we have an HTTP response?
        response.unauthorized()

    security.declarePrivate( 'resetCredentials' )
    def resetCredentials( self, request, response ):

        """ Raise unauthorized to tell browser to clear credentials.
        """
        # XXX:  Does this need to check whether we have an HTTP response?
        response.unauthorized()

InitializeClass( HTTPBasicAuthHelper )
