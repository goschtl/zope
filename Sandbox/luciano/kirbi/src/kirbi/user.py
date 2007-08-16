import grok
from interfaces import IUser
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.interface import Interface, implements, invariant, Invalid
from zope import schema
import sha
import app

class UserFolder(grok.Container):
    implements(IAuthenticatorPlugin)

    def principalInfo(self, id):
        """Find a principal given an id"""
        if id in self:
            # in Kirbi, the login and the id are the same
            return IPrincipalInfo(self[id])
        
    def authenticateCredentials(self, credentials):
        """Authenticate a principal"""
        id = credentials['login']
        user = self.get(id)
        if user is not None:
            given_hash = sha.new(credentials['password']).hexdigest()
            if user.password == given_hash:
                return IPrincipalInfo(self[id])

class User(grok.Container):
    """A Kirbi user implementation.

    A User will contain Copy instances, representing book copies
    owned by the user.

        >>> alice = User('alice', u'Alice Cooper', u'headless-chicken')
        >>> IUser.providedBy(alice)
        True
        >>> alice.password
        'f030ff587c602e0e9a68aba75f41c51a0dc22c62'
        >>> alice.name_and_login()
        u'Alice Cooper (alice)'
    """

    implements(IUser)

    login = u''
    name = u''
    password = ''

    def __init__(self, login, name, password):
        super(User, self).__init__()
        self.login = login
        self.name = name
        self.password = sha.new(password).hexdigest()

    def name_and_login(self):
        if self.name:
            return '%s (%s)' % (self.name, self.login)
        else:
            return self.login

class Index(grok.View):
    grok.context(User)

class PrincipalInfoAdapter(grok.Adapter):
    grok.context(User)
    grok.implements(IPrincipalInfo)

    def __init__(self, context):
        self.context = context

    def getId(self):
        return self.context.login

    def setId(self, id):
        self.context.login = id

    id = property(getId, setId)

    def getTitle(self):
        return self.context.name

    def setTitle(self, title):
        self.context.name = title

    title = property(getTitle, setTitle)

    @property
    def description(self):
        return self.context.name_and_login()

class UserSearch(grok.View):
    grok.context(UserFolder)
    grok.name('index')

    def update(self, query=None):
        self.results_title = '%d users' % len(self.context)

class Login(grok.View):
    grok.context(UserFolder)
    def render(self):
        return 'This should log you in...'

class Logout(grok.View):
    grok.context(UserFolder)
    def render(self):
        return "This should log you out (but doesn't yet)."

class Join(grok.AddForm):
    grok.context(UserFolder)
    """User registration form"""

    form_fields = grok.AutoFields(IUser)

    @grok.action('Add entry')
    def add(self, **data):
        login = data['login']
        self.context[login] = User(**data)
        self.redirect(self.url(login))

