##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""
$Id: field.py,v 1.3 2003/01/10 19:38:48 stevea Exp $
"""

from zope.schema.interfaces import IField
from zope.app.component.interfacefield import InterfaceField
from zope.interface import Interface

class IComponentRelated(Interface):
    'An interface for something that is related to a single component.'

    type = InterfaceField(
        title = u"An interface that must be implemented by the component.",
        required = True,
        readonly = True,
        basetype = None
        )

class IComponentLocation(IComponentRelated, IField):
    '''A field containing a component location.

    This is as an absolute path, or as a dotted module name.'''


class IComponentPath(IComponentRelated, IField):
    'A field containing a component path.'

