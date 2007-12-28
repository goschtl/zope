from zope.interface import Interface
from zope import schema

class IUser(Interface):
    """Basic user data."""
    login = schema.TextLine(title=u"Login",
                            required=True)
    password = schema.Password(title=u"Password",
                            required=True)
    name = schema.TextLine(title=u"Real name",
                            required=False)
    email = schema.ASCIILine(title=u"E-mail",
                            required=False)
