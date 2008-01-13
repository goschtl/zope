import grok

from urllib import urlencode

from zope.interface import Interface, implements
from zope.component import getUtility, getUtilitiesFor
from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.interfaces import IPasswordManager
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.principalfolder import IInternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.schema.interfaces import IField, IIterableSource
from zope.i18n import MessageFactory

_ = MessageFactory('logindemo')

def setup_pau(pau):
    '''
    Callback to setup the Pluggable Authentication Utility
    
    A reference to this function is passed as a parameter in the
    declaration of the PAU (see LoginDemo class)
    '''
    # the principal source is a PrincipalFolder, stored in ZODB
    pau['principals'] = PrincipalFolder() 
    pau.authenticatorPlugins = ('principals',)
    # the SessionCredentialsPlugin isused for cookie-based authentication
    pau['session'] = session = SessionCredentialsPlugin()
    session.loginpagename = 'login' # the page to redirect for login
    # configuration of the credentials plugin
    pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
        
class LoginDemo(grok.Application, grok.Container):
    """
    An app that lets users create accounts, login, logout and change their
    passwords.
    """
    # register the authentication utility; see setup_pau for settings
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
           
class ViewMemberListing(grok.Permission):
    ''' Permission to see the member listing '''
    grok.name('logindemo.ViewMemberListing')

class Master(grok.View):
    """
    The master page template macro.
    
    The template master.pt is used as page macro in most views. Since this
    template uses the logged_in method and message attributes below, it's best
    to make all other views in this app subclasses of Master.
    """
    grok.context(Interface)  # register this view for all objects

    message = '' # used to give feedback

    def logged_in(self):
        # this is the canonical way to tell whether the user is authenticated
        # in Zope 3: check if the principal provides IUnauthenticatedPrincipal
        return not IUnauthenticatedPrincipal.providedBy(self.request.principal)
    
class Index(Master):
    """
    The main page, showing user data and member count.
    """

    def members(self):
        # get the authentication utility
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
        if login_submit is not None: # we are handling the login submission
            if self.logged_in(): # if the login was accepted then...
                # redirect to where the user came from, or to the main page
                dest = self.request.get('camefrom', self.application_url())
                self.redirect(dest)
            else: # if the user is still not logged in...
                # then an incorrect login or password was provided
                self.message = _(u'Invalid login name and/or password')

class Logout(grok.View):
    """
    Logout handler.
    """
    grok.context(Interface)
    def render(self):
        # get the session plugin and tell it to logout
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        # redirect to the main page
        self.redirect(self.application_url())
        
class Join(grok.AddForm, Master):
    """
    User registration form.
    """
    form_fields = grok.AutoFields(IInternalPrincipal)
    label = u'User registration'
    template = grok.PageTemplateFile('form.pt')
    
    @grok.action('Save')
    def save(self, **data):
        '''
        Create an InternalPrincipal with the user data.
        
        This method also grants the ViewMemberListing permission to the user.
        '''
        login = data['login']
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        # create an instance of InternalPrincipal
        principal = InternalPrincipal(**data)
        # XXX: the login name must be unique; need better handling of this
        assert(login not in principals)
        principals[login] = principal
        # grant the user permission to view the member listing
        permission_mngr = IPrincipalPermissionManager(grok.getSite())
        permission_mngr.grantPermissionToPrincipal(
           'logindemo.ViewMemberListing', principals.prefix + login)

        self.redirect(self.url('login')+'?'+urlencode({'login':login}))
                    
class Account(grok.View):
    
    def render(self):
        return 'Not implemented'
    
class Listing(Master):
    '''
    Member listing view.
    
    This demonstrates how to require a permission to view, and also how to
    obtain a list of annotated principals.
    '''

    grok.require('logindemo.ViewMemberListing')

    def fieldNames(self):
        # failed attempt to list fields but not methods; this returns empty
        # return (f for f in IInternalPrincipal if IField.providedBy(f))
        
        # another failed attempt to list fields but not methods; this returns
        # all attributes 
        # return (f for f in IInternalPrincipal if not callable(f))
        
        return ['login', 'title', 'description']

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        roster = []
        for id in sorted(principals.keys()):
            user = principals[id]
            fields = {}
            for field in self.fieldNames():
                fields[field] = getattr(user, field)
            roster.append(fields)
        return roster

class PasswordManagerChoices(object):
    implements(IIterableSource)
    
    def __init__(self):
        self.choices = [name for name, util in
                            sorted(getUtilitiesFor(IPasswordManager))]
        
    def __iter__(self):
        return iter(self.choices)
    
    def __len__(self):
        return len(self.choices)
    
    def __contains__(self, value):
        return value in self.choices
    