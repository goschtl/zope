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

$Id: message.py 230 2007-05-04 03:17:36Z srichter $
"""
__docformat__ = "reStructuredText"
import persistent
import zope.interface
from zope.location import location
from zope.schema import fieldproperty
from z3c.formjsdemo.message import interfaces

class HelloWorld(location.Location, persistent.Persistent):
    zope.interface.implements(interfaces.IHelloWorld)

    who = fieldproperty.FieldProperty(interfaces.IHelloWorld['who'])
    when = fieldproperty.FieldProperty(interfaces.IHelloWorld['when'])
    what = fieldproperty.FieldProperty(interfaces.IHelloWorld['what'])

    def __init__(self, who, when, what):
        self.who = who
        self.when = when
        self.what = what

    def __repr__(self):
        return '<%s from %r>' %(self.__class__.__name__, self.who)
