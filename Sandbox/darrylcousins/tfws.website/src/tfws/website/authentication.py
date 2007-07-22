import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.authentication.simple import member

from tfws.website import interfaces

class WebSiteMember(member.Member):
    """An IMember for MemberContainer."""

    zope.interface.implements(interfaces.IWebSiteMember)

    firstName = FieldProperty(interfaces.IWebSiteMember['firstName'])
    lastName = FieldProperty(interfaces.IWebSiteMember['lastName'])
    email = FieldProperty(interfaces.IWebSiteMember['email'])

    def __init__(self, login, password, firstName, lastName, email):
        title = firstName +' '+ lastName
        super(WebSiteMember, self).__init__(login, password, title)
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.description = email

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.title)
