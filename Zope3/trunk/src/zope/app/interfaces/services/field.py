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
$Id: field.py,v 1.1 2003/01/09 19:13:48 stevea Exp $
"""

from zope.schema.interfaces import IField
from zope.app.component.interfacefield import InterfaceField

class IComponentPath(IField):
    'A field containing a component path.'

    type = InterfaceField(
        title = u"An interface that must be implemented by the component.",
        required = True,
        readonly = True,
        basetype = None
        )

