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
"""Message Board Tests

$Id: test_message.py,v 1.2 2003/08/20 17:07:46 srichter Exp $
"""
import unittest
from zope.interface import classImplements 
from zope.testing.doctestunit import DocTestSuite

from zope.app.annotation.interfaces import IAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.container.tests.test_icontainer import TestSampleContainer
from zope.app.location import LocationPhysicallyLocatable
from zope.app.location.interfaces import ILocation
from zope.app.tests import placelesssetup
from zope.app.tests import ztapi
from zope.app.traversing.interfaces import IPhysicallyLocatable

from book.messageboard.interfaces import IMailSubscriptions
from book.messageboard.interfaces import IMessage
from book.messageboard.message import MailSubscriptions
from book.messageboard.message import Message


class Test(TestSampleContainer):

    def makeTestObject(self):
        return Message()


def setUp():
    placelesssetup.setUp()
    classImplements(Message, IAttributeAnnotatable)
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)
    ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)
    ztapi.provideAdapter(IMessage, IMailSubscriptions, MailSubscriptions)

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('book.messageboard.message',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
