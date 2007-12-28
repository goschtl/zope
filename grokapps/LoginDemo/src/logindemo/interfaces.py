import re

from zope.interface import Interface
from zope import schema
from zope.i18n import MessageFactory

_ = MessageFactory('logindemo')

class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True

class IUser(Interface):
    """Basic user data."""
    login = schema.TextLine(title=u"Login",
                            required=True)
    password = schema.Password(title=u"Password",
                            required=True)
    name = schema.TextLine(title=u"Real name",
                            required=False)
    email = schema.ASCIILine(title=u"E-mail",
                            required=False,
                            constraint=validate_email)
