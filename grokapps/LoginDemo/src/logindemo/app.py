import grok

from urllib import urlencode

from zope.interface import Interface
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.role import LocalRole
from zope.component import getUtility



from logindemo.interfaces import IUser

def setup_pau(pau):
    pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals',)
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login'
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)

def role_factory(*args):
    def factory():
        return LocalRole(*args)
    return factory

class LoginDemo(grok.Application, grok.Container):
    """
    An app that lets you create an account and change your password.
    """
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    grok.local_utility(role_factory(u'Site Member'), IRole,
                       name='logindemo.member',
                       name_in_container='logindemo.member')

class Index(grok.View):
    """
    The main page, where the user can login or click a link to join.
    """
    
    def logged_in(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)

class Login(grok.View):
    grok.context(Interface)
    
    message = '' # used to give feedback on failed logins

    def update(self, login_submit=None):
        # XXX: need to display some kind of feedback when the login fails
        if login_submit is not None:
            if IUnauthenticatedPrincipal.providedBy(self.request.principal):
                self.message = u'Invalid login name and/or password'
            else:
                destination = self.request.get('camefrom', self.application_url())
                self.redirect(destination)

class Logout(grok.View):
    grok.context(Interface)
    def render(self):
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        self.redirect(self.application_url())
        
class Join(grok.AddForm):
    """User registration form"""

    form_fields = grok.AutoFields(IUser)
    #template = grok.PageTemplateFile('form.pt')
    form_title = u'User registration'

    @grok.action('Save')
    def join(self, **data):
        login = data['login']
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        if login in principals: # duplicate login name
            ### XXX: find out how to display this message in the form template
            msg = u'Duplicate login. Please choose a different one.'
            self.redirect(self.url()+'?'+urlencode({'error_msg':msg}))
        else:
            # add principal to principal folder
            principals[login] = InternalPrincipal(login, data['password'],
                                                  data['name'])    
            # assign role to principal
            role_manager = IPrincipalRoleManager(self.context)
            role_manager.assignRoleToPrincipal('logindemo.member', 
                                   principals.prefix + login)
            self.redirect(self.url('login')+'?'+urlencode({'login':login}))

        