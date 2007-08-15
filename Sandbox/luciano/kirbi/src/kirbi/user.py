import grok
from interfaces import IUser
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.interface import Interface, implements, invariant, Invalid
from zope import schema
import sha

class UserFolder(grok.Container):
    pass

class User(grok.Container):
    """A Kirbi user implementation.

    A User will contain Copy instances, representing book copies
    owned by the user.

        >>> alice = User('alice', u'Alice Cooper', u'headless-chicken')
        >>> IUser.providedBy(alice)
        True
        >>> alice.passwordHash()
        'f030ff587c602e0e9a68aba75f41c51a0dc22c62'
        >>> alice.name_and_login()
        u'Alice Cooper (alice)'
    """

    implements(IUser)

    login = u''
    name = u''
    password = u''

    def __init__(self, login, name, password):
        super(User, self).__init__()
        self.login = login
        self.name = name
        self.password = password

    def passwordHash(self):
        return sha.new(self.password).hexdigest()

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


class UserAuthenticationPlugin(object):
    """Simple authentication and search plugin"""
    implements(IAuthenticatorPlugin)

    principals = (
        {'id':'alice', 'login':'alice', 'password':'123'},
        {'id':'bob', 'login':'bob', 'password':'123'}
        )

    prefix = "" # principal id prefix

    def principalInfo(self, id):
        """Find a principal given an id"""
        for principal in self.principals:
            if self.prefix + "." + principal['id'] == id:
                return {'login' : principal['login']}

    def authenticateCredentials(self, credentials):
        """Authenticate a principal"""
        for principal in self.principals:
            if credentials['login']==principal['login'] and \
               credentials['password']==principal['password']:
                return (self.prefix + "." + principal['id'],
                         {'login' : principal['login']})
