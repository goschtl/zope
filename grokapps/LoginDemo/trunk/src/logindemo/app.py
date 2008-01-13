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
    An app that lets you create an account and change your password.
    """
    # register the authentication utility; see setup_pau for settings
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    # make InternalPrincipal instances annotatable
    classImplements(InternalPrincipal,IAttributeAnnotatable)
    # register the adapter for IInternalPrincipal which provides IUser
    provideAdapter(UserDataAdapter)
           
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
    form_fields = grok.AutoFields(IUser)
    # XXX: Failed attempt to display the password_encoding field
    #form_fields[u'password_encoding'].custom_widget = SourceDropdownWidget
    label = u'User registration'
    template = grok.PageTemplateFile('form.pt')
    
    @grok.action('Save')
    def save(self, **data):
        '''
        Create an InternalPrincipal with the user data.
        
        This method also sets extra fields using an annotations through
        the IUser adapter, and grants the ViewMemberListing permission to
        the principal just created.
        '''
        login = data['login']
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        # create an instance of InternalPrincipal
        principal = InternalPrincipal(login, data['password'], data['name'],
                                      passwordManagerName='SHA1')
        # add principal to principal folder; we may assume that the login
        # name is unique because of validation on the IUser interface
        # but to be doubly sure, we assert this
        assert(login not in principals)
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
    '''
    Member listing view.
    
    This demonstrates how to require a permission to view, and also how to
    obtain a list of annotated principals.
    '''

    grok.require('logindemo.ViewMemberListing')

    def fieldNames(self):
        return (f for f in IUser)

    def members(self):
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        roster = []
        for id in sorted(principals.keys()):
            # adapt the principals to IUser to get all fields
            user = IUser(principals[id])
            fields = {}
            for field in IUser:
                fields[field] = getattr(user, field)
            roster.append(fields)
        return roster
