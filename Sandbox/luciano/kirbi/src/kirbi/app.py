import grok
from grok import index
from kirbi.pac import Pac
from kirbi.book import Book
from kirbi.user import User, UserFolder
from kirbi.interfaces import IUser
from zope.interface import Interface, implements
from zope.component import getSiteManager
from zope.traversing import browser
from urllib import urlencode

from zope.app.authentication import PluggableAuthentication
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import InternalPrincipal
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager, IRole
from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.role import LocalRole
from zope import schema
from zope.component import getUtility

PAC_NAME = u'pac'
USER_FOLDER_NAME = u'u'

grok.define_permission('kirbi.AddCopy')
grok.define_permission('kirbi.ManageBook')

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

class Kirbi(grok.Application, grok.Container):
    """Peer-to-peer library system."""
    grok.local_utility(PluggableAuthentication, IAuthentication,
                       setup=setup_pau)
    grok.local_utility(role_factory(u'Book Owner'), IRole,
                       name='kirbi.Owner',
                       name_in_container='kirbi.Owner')
    def __init__(self):
        super(Kirbi, self).__init__()
        self.pac = self[PAC_NAME] = Pac()
        self.userFolder = self[USER_FOLDER_NAME] = UserFolder()

@grok.subscribe(Kirbi, grok.IObjectAddedEvent)
def grant_permissions(app, event):
    role_manager = IRolePermissionManager(app)
    role_manager.grantPermissionToRole('kirbi.AddCopy', 'kirbi.Owner')
    role_manager.grantPermissionToRole('kirbi.ManageBook', 'kirbi.Owner')

class Index(grok.View):

    def pac_url(self):
        return self.url(self.context.pac)

    def login_url(self):
        return self.url(self.context.userFolder,'login')

class BookIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(Book)

    title = index.Text()
    isbn13 = index.Field()
    searchableText = index.Text()

    creatorsSet = index.Set()

class Master(grok.View):
    """The master page template macro."""
    # register this view for all objects
    grok.context(Interface)

class Login(grok.View):
    grok.context(Interface)

    def update(self, login_submit=None, login=None):
        # XXX: need to display some kind of feedback when the login fails
        if (not IUnauthenticatedPrincipal.providedBy(self.request.principal)
            and login_submit is not None):
            destination = self.request.get('camefrom')
            if not destination:
                destination = self.application_url()
            self.redirect(destination)

class Logout(grok.View):
    grok.context(Interface)
    def render(self):
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        self.redirect(self.application_url())

class Join(grok.AddForm):
    """User registration form"""
    grok.context(Kirbi)

    form_fields = grok.AutoFields(IUser)
    template = grok.PageTemplateFile('form.pt')
    form_title = u'User registration'

    ### XXX: find out how to display message of the Invalid exception raised
    ### by the password confirmation invariant (see interfaces.IUser)
    @grok.action('Save')
    def join(self, **data):
        #XXX: change this method to use our UserFolder and User class instead
        #     of PrincipalFolder and InternalPrincipal
        login = data['login']
        self.context[login] = User(**data)
    
        # add principal to principal folder
        pau = getUtility(IAuthentication)
        principals = pau['principals']
        principals[login] = InternalPrincipal(login, data['password'],
                                              data['name'])

        # assign role to principal
        role_manager = IPrincipalRoleManager(self.context)
        role_manager.assignRoleToPrincipal('kirbi.Owner', 
                               principals.prefix + login)
        self.redirect(self.url('login')+'?'+urlencode({'login':login}))
 