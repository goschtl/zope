###############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id: authentication.py 371 2007-03-26 01:44:30Z roger.ineichen $
"""

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.authentication.simple import member
from z3c.website import interfaces


class WebSiteMember(member.Member):
    """An IMember for MemberContainer."""

    zope.interface.implements(interfaces.IWebSiteMember)

    firstName = FieldProperty(interfaces.IWebSiteMember['firstName'])
    lastName = FieldProperty(interfaces.IWebSiteMember['lastName'])
    email = FieldProperty(interfaces.IWebSiteMember['email'])
    phone = FieldProperty(interfaces.IWebSiteMember['phone'])

    def __init__(self, login, password, firstName, lastName, email):
        title = firstName +' '+ lastName
        super(WebSiteMember, self).__init__(login, password, title)
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.description = email

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.title)
