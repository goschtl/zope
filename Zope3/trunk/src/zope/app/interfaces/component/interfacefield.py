##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""These are the interfaces for the common fields.

$Id: interfacefield.py,v 1.5 2003/04/14 18:21:35 fdrake Exp $
"""

from zope.interface import Interface
from zope.schema import Field
from zope.schema.interfaces import IEnumerated, IField, ITuple

class IInterfaceField(IEnumerated, IField):
    u"""A type of Field that has an Interfaces as its value."""

    basetype = Field(
        title=u"Base type",
        description=(u"All values must extend (or be) this type,"
                     u" unless it is None which means 'anything'."),
        default=Interface,
        )

class IInterfacesField(ITuple):
    u"""A type of Field that is has a tuple of Interfaces as its value."""

    basetype = Field(
            title=u"Base type",
            description=(u"All values must extend or be this type,"
                         u" unless it is None, which means 'anything'."),
            default=Interface,
            )
