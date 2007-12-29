import grok

from urllib import urlencode

from zope.interface import Interface
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.component import getUtility
from zope.i18n import MessageFactory

from logindemo.interfaces import IUser

_ = MessageFactory('logindemo')

def setup_pau(pau):
    pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals',)
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login'
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
        
class ViewMemberListing(grok.Permission):
    grok.name('logindemo.ViewMemberListing')

class LoginDemo(grok.Application, grok.Container):
    """
    An app that lets you create an account and change your password.
    """
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    
class Master(grok.View):
    """
    The master page template macro.
    """
    grok.context(Interface)  # register this view for all objects

    message = '' # used to give feedback

    def logged_in(self):
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)
    
class Index(Master):
    """
    The main page, where the user can login or click a link to join.
    """

    def members(self):
        pau = getUtility(IAuthentication)
        result = len(pau['principals'])
        if result == 0:
            return _(u'No one has')
        elif result == 1:
            return _(u'One member has')
        else:
            return unicode(result) + _(u' members have')

    
class Login(Master):
    """
    Login form and handler.
    """
    def update(self, login_submit=None):
        if login_submit is not None:
            if IUnauthenticatedPrincipal.providedBy(self.request.principal):
                self.message = _(u'Invalid login name and/or password')
            else:
                destination = self.request.get('camefrom', self.application_url())
                self.redirect(destination)

class Logout(grok.View):
    """
    Logout handler.
    """
    grok.context(Interface)
    def render(self):
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        self.redirect(self.application_url())
        
class Join(grok.AddForm):
    """
    User registration form.
    """
    form_fields = grok.AutoFields(IUser)
    form_title = u'User registration'

    @grok.action('Save')
    def join(self, **data):
        login = data['login']
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        if login in principals: # duplicate login name
            ### XXX: find out how to display this message in the form template
            msg = _(u'Duplicate login. Please choose a different one.')
            self.redirect(self.url()+'?'+urlencode({'error_msg':msg}))
        else:
            # add principal to principal folder
            principals[login] = InternalPrincipal(login, data['password'],
                                                  data['name'])                
            # grant the user permission to view the member listing
            permission_mngr = IPrincipalPermissionManager(grok.getSite())
            permission_mngr.grantPermissionToPrincipal(
               'logindemo.ViewMemberListing', principals.prefix + login)

            self.redirect(self.url('login')+'?'+urlencode({'login':login}))

class Account(grok.View):
    
    def render(self):
        return 'Not implemented'
    
class Listing(Master):
    grok.require('logindemo.ViewMemberListing')

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        return [{'id':id, 'title':principals[id].title}
            for id in sorted(principals.keys())]       
