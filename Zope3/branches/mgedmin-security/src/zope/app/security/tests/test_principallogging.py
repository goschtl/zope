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
"""Test for PrincipalLogging.

$Id: test_principallogging.py,v 1.3 2004/03/08 12:06:02 srichter Exp $
"""
import unittest
from zope.interface.verify import verifyObject

class PrincipalStub:

    id = 42


class TestPrincipalLogging(unittest.TestCase):

    def test_interface(self):
        from zope.app.security.principallogging import PrincipalLogging
        from zope.publisher.interfaces.logginginfo import ILoggingInfo
        principal = PrincipalStub()
        pl = PrincipalLogging(principal)
        verifyObject(ILoggingInfo, pl)

    def test_getLogMessage(self):
        from zope.app.security.principallogging import PrincipalLogging
        principal = PrincipalStub()
        pl = PrincipalLogging(principal)
        self.assertEquals(pl.getLogMessage(), "42")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPrincipalLogging))
    return suite


if __name__ == '__main__':
    unittest.main()
