import grok

from urllib import urlencode

from zope.interface import Interface, implements, classImplements
from zope.component import getUtility, provideAdapter
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
# XXX: Failed attempt to display the password_encoding field
# from zope.app.form.browser.source import SourceDropdownWidget
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.i18n import MessageFactory

from interfaces import IUser, UserDataAdapter  

_ = MessageFactory('logindemo')

def setup_pau(pau):
    pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals',)
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login'
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
        
class LoginDemo(grok.Application, grok.Container):
    """
    An app that lets you create an account and change your password.
    """
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    # make InternalPrincipal instances annotatable
    classImplements(InternalPrincipal,IAttributeAnnotatable)
    # register the adapter for IInternalPrincipal which provides IUser
    provideAdapter(UserDataAdapter)
           
class ViewMemberListing(grok.Permission):
    grok.name('logindemo.ViewMemberListing')

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
    The main page, showing user data and member count.
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
        
class Join(grok.AddForm, Master):
    """
    User registration form.
    """
    form_fields = grok.AutoFields(IUser)
    # XXX: Failed attempt to display the password_encoding field
    #form_fields[u'password_encoding'].custom_widget = SourceDropdownWidget
    form_title = u'User registration'
    template = grok.PageTemplateFile('form.pt')
    
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
            principal = InternalPrincipal(login, data['password'], data['name'],
                                          passwordManagerName='SHA1')
            # add principal to principal folder
            principals[login] = principal
            # save the e-mail
            user = IUser(principal)
            user.email = data['email']
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

    def fieldNames(self):
        return (f for f in IUser)

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        roster = []
        for id in sorted(principals.keys()):
            user = IUser(principals[id])
            fields = {}
            for field in IUser:
                fields[field] = getattr(user, field)
            roster.append(fields)
        return roster
