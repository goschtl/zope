##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Schema Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.app.schema import schema

from zope.webdev import interfaces

class Schema(schema.SchemaUtility):
    """Special Persistent Schema that is more schema-driven."""
    zope.interface.implements(interfaces.ISchema)

    name = property(schema.SchemaUtility.getName,
                     schema.SchemaUtility.setName)

    bases = schema.SchemaUtility.__bases__

    @apply
    def docstring():

        def get(self):
            return self.__docstring__

        def set(self, value):
            self.__docstring__ = value

        return property(get, set)

    def __init__(self, name, bases=(), docstring=None):
        super(Schema, self).__init__(name, bases, __doc__=docstring)
