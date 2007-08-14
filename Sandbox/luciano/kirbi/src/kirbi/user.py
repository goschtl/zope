import grok
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.interface import Interface, implements, invariant, Invalid
from zope import schema
import sha

class UserFolder(grok.Container):
    pass

class IUser(Interface):
    """A Kirbi user"""
    login = schema.TextLine(title=u"Login",
                            required=True)
    name = schema.TextLine(title=u"Name",
                            required=False)
    password = schema.Password(title=u"Password",
                            required=True)
    
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
    
class Index(grok.View):
    grok.context(UserFolder)
    def update(self, query=None):
        self.results_title = '%d users' % len(self.context)
    
class Register(grok.AddForm):
    grok.context(UserFolder)
    """User registration form"""
    
    form_fields = grok.AutoFields(IUser)

    @grok.action('Add entry')
    def add(self, **data):
        self.context[data['login']] = User(**data)
        self.redirect(self.url('u'))

