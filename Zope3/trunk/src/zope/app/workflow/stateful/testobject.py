##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Stateful Workflow Test Object

This represents a simple content object that can receive workflows.

$Id: testobject.py,v 1.1 2003/07/31 15:01:36 srichter Exp $
"""

from persistence import Persistent
from zope.interface import Interface, implements
from zope.schema import TextLine, Int

class ITestObject(Interface):

    test = TextLine(
        title=u"Test Attribute",
        description=u"This is a test attribute.",
        default=u"foo",
        required=True)

class IWorkflowData(Interface):

    title = TextLine(
        title=u"Title",
        required=True)

    number = Int(
        title=u"Number",
        required=True)


class TestObject(Persistent):
    implements(ITestObject)

    test = u"foo"

