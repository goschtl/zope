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

$Id: interfacefield.py,v 1.3 2002/12/30 18:43:07 stevea Exp $
"""

from zope.schema import Field
from zope.schema.interfaces import IValueSet, ITuple
from zope.interface import Interface

class IInterfaceField(IValueSet):
    u"""A type of Field that has an Interfaces as its value."""

    type = Field(title=u"Base type",
                 description=u"All values must extend (or be) this type",
                 default=Interface,
                 )

class IInterfacesField(ITuple):
    u"""A type of Field that is has a tuple of Interfaces as its value."""

    value_types = Field(
            title=u"Base type",
            description=u"All values must extend or be these types",
            default=(Interface,),
            )
