import grok
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.interface import implements, invariant, Invalid
import sha

class UserFolder(grok.Container):
    pass

class User(object):
    """
    A Kirbi user. To implement IPrincipalInfo but still use more familiar
    attribute names, we use properties to make ``id`` the same as ``login``
    and ``title`` the same as ``name``.

    >>> alice = User('alice', u'Vincent Damon Furnier', u'headless-chicken')
    >>> alice.id, alice.title, alice.description
    ("alice", u"Vincent Damon Furnier", u"Vincent Damon Furnier (alice)")
    
    >>> alice.title = u'Alice Cooper'
    >>> alice.name
    u"Alice Cooper"
    
    >>> alice.passwd_hash
    ABC

    """

    implements(IPrincipalInfo)
    
    login = ''
    name = ''
    passwd_hash = ''
        
    def __init__(self, login, name, passwd):
        self.login = login
        self.name = name
        self.passwd = sha.new(passwd).hexdigest()

    def getId(self):
        return self.login

    def setId(self, id):
        self.login = id

    id = property(getId, setId)

    def getTitle(self):
        return self.name

    def setTitle(self, title):
        self.name = title

    id = property(getId, setId)

    @property
    def description(self):
        return '%s (%s)' % (self.name, self.login)
    
    
        


class Index(grok.View):
    grok.context(UserFolder)
    def update(self, query=None):
        self.results_title = '%d users' % len(self.context)

    
class Register(grok.AddForm):
    grok.context(UserFolder)
    """ User registration form """
    
    form_fields = grok.AutoFields(IPrincipalInfo)

    @grok.action('Add entry')
    def add(self, **data):
        self.context[id] = User(**data)
        self.redirect(self.url('users'))

