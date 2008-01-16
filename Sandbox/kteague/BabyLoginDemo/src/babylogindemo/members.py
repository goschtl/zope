import grok

from zope.interface import implements, Interface
from zope.schema import TextLine, Password, Text
from zope.i18n import MessageFactory
from zope.security.interfaces import IPrincipal

_ = MessageFactory('babylogindemo')

class IMember(Interface):
    login = TextLine(
        title=_("Login"),
        description=_("Unique Id")
    )
    password = Password(
        title=_("Password"),
        description=_("The password. It is in plain-text, whee!")
    )
    title = TextLine(
        title=_("Full Name"),
    )
    description = Text(
        title=_("Description"),
        description=_("Tell us a little bit about yourself."),
        required=False,
        missing_value='',
        default=u''
    )


class Member(grok.Model):
    implements(IMember, IPrincipal)

    def __init__(self, login, password, title, description=''):
        self.login = login
        self.password = password
        self.title = title
        self.description = description
    
    @property
    def id(self):
        return self.login
