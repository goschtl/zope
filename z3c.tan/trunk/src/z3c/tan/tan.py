##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""TAN Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
from zope.app.container import contained
from zope.schema.fieldproperty import FieldProperty

from z3c.tan import interfaces


class TANInformation(contained.Contained, persistent.Persistent):
    zope.interface.implements(interfaces.ITANInformation)

    tan = FieldProperty(
        interfaces.ITANInformation['tan'])
    title = FieldProperty(
        interfaces.ITANInformation['title'])
    description = FieldProperty(
        interfaces.ITANInformation['description'])
    allowedPrincipals = FieldProperty(
        interfaces.ITANInformation['allowedPrincipals'])

    def __init__(self, tan, title=None, description=None):
        self.id = tan
        self.tan = tan
        self.title = title
        self.description = description
        self.allowedPrincipals = None

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.tan)
