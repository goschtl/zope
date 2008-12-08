import martian
import grok
import megrok.login
from zope import component

from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from megrok.login.authplugins import PrincipalRegistryAuthenticator

class ApplicationGrokker(martian.ClassGrokker):
    martian.component(grok.Site)
    martian.priority(100)
    martian.directive(megrok.login.enable, default=False)
    martian.directive(megrok.login.viewname, default=u'loginForm.html')
    martian.directive(megrok.login.strict, default=False)
    
    def execute(self, factory, config, enable, viewname, strict, **kw):
        if enable is False:
            return False
        adapts = (factory, grok.IObjectAddedEvent)
        config.action(
            discriminator=None,
            callable=component.provideHandler,
            args=(authenticationSubscriber, adapts)
            )
        return True

def authenticationSubscriber(site, event):
    grok.meta.setupUtility(site, PluggableAuthentication(), IAuthentication,
                           setup=setupPAU,
                           name_in_container='megrok_login_pau')


def setupPAU(pau):
    """Callback to setup the Pluggable Authentication Utility """
    site = pau.__parent__.__parent__
    viewname = megrok.login.component.viewname.bind().get(site)
    strict = megrok.login.component.strict.bind().get(site)

    pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals', )
    if strict is False:
        pau['readonly_principals'] = PrincipalRegistryAuthenticator()
        pau.authenticatorPlugins = ('principals', 'readonly_principals')

    pau['session'] = session = SessionCredentialsPlugin()
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
    session.loginpagename = viewname
