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
from zope.testing.doctestunit import DocTestSuite

from zope.app.container.tests.test_icontainer import TestSampleContainer

from book.messageboard.message import Message


class Test(TestSampleContainer):

    def makeTestObject(self):
        return Message()

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('book.messageboard.message'),
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
