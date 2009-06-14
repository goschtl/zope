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
"""Hello Worl Message Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
from zope.location import location
from zope.schema import fieldproperty
from z3c.formdemo.message import interfaces

class HelloWorld(location.Location, persistent.Persistent):
    zope.interface.implements(interfaces.IHelloWorld)

    who = fieldproperty.FieldProperty(interfaces.IHelloWorld['who'])
    when = fieldproperty.FieldProperty(interfaces.IHelloWorld['when'])
    what = fieldproperty.FieldProperty(interfaces.IHelloWorld['what'])

    def __init__(self, who, when, what):
        self.who = who
        self.when = when
        self.what = what
