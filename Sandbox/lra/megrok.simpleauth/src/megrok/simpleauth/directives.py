from zope.app.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.session import SessionCredentialsPlugin

from grok.directive import MultipleTimesDirective, ClassDirectiveContext, LocalUtilityInfo

def setup_pau(pau):
    '''
    Callback to setup the Pluggable Authentication Utility
    
    A reference to this function is passed as a parameter in the
    declaration of the PAU (see PlainLoginDemo class)
    '''
    # the principal source is a PrincipalFolder, stored in ZODB
    pau['principals'] = PrincipalFolder() 
    pau.authenticatorPlugins = ('principals',)
    # the SessionCredentialsPlugin isused for cookie-based authentication
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login' # the page to redirect for login
    # configuration of the credentials plugin
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)

class SetupAuthenticationDirective(MultipleTimesDirective):
    def check_arguments(self):
        pass
        
    def value_factory(self):
        
        return LocalUtilityInfo(PluggableAuthentication, provides=IAuthentication, name=u'',
                     setup=setup_pau, public=False, name_in_container=None)
    
setup_authentication_if_it_pleases_you_mr_grok = SetupAuthenticationDirective('grok.local_utility',
                                      ClassDirectiveContext())