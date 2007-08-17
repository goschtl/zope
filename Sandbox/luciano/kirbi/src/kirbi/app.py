import grok
from grok import index
from kirbi.pac import Pac
from kirbi.book import Book
from kirbi.user import UserFolder
from zope.interface import Interface, implements
from zope.component import getSiteManager
from zope.traversing import browser

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

PAC_NAME = u'pac'
USER_FOLDER_NAME = u'u'

grok.define_permission('kirbi.Join')
grok.define_permission('kirbi.EditBook')
grok.define_permission('kirbi.DeleteBook')

def setup_pau(pau):
    pau['principals'] = PrincipalFolder('kirbi.principals.')
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
        global sitePac, siteUsers, siteUsersURL
        super(Kirbi, self).__init__()
        self.pac = self[PAC_NAME] = Pac()
        self.user_folder = self[USER_FOLDER_NAME] = UserFolder()

@grok.subscribe(Kirbi, grok.IObjectAddedEvent)
def grant_permissions(app, event):
    role_manager = IRolePermissionManager(app)
    role_manager.grantPermissionToRole('kirbi.EditBook', 'kirbi.Owner')

class Index(grok.View):

    def pac_url(self):
        return self.url(self.context.pac)

    def login_url(self):
        return self.url(self.context.user_folder,'login')

class BookIndexes(grok.Indexes):
    grok.site(Kirbi)
    grok.context(Book)

    title = index.Text()
    isbn13 = index.Field()
    searchableText = index.Text()

    #XXX: check whether this is working:
    # the creatorSet book method was not being called
    creatorsSet = index.Set()

class Master(grok.View):
    """The master page template macro."""
    # register this view for all objects
    grok.context(Interface)

class Login(grok.View):
    grok.context(Interface)

    def update(self, login_submit=None):
        if (not IUnauthenticatedPrincipal.providedBy(self.request.principal)
            and login_submit is not None):
            camefrom = self.request.get('camefrom', '.')
            self.redirect(camefrom)

class Logout(grok.View):
    grok.context(Interface)
    def render(self):
        return "This should log you out (but doesn't yet)."
