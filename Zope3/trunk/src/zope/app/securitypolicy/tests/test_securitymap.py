##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################
"""
$Id$
"""
import unittest
from zope.interface.verify import verifyClass
from zope.app.securitypolicy.interfaces import ISecurityMap
from zope.app.securitypolicy.securitymap import SecurityMap
from zope.app.securitypolicy.securitymap import PersistentSecurityMap

class TestSecurityMap(unittest.TestCase):

    def testInterface(self):
        verifyClass(ISecurityMap, SecurityMap)

    # XXX Test the map. Grrrrr.

class TestPersistentSecurityMap(TestSecurityMap):

    def testInterface(self):
        verifyClass(ISecurityMap, PersistentSecurityMap)

    # XXX test persistence...


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSecurityMap),
        unittest.makeSuite(TestPersistentSecurityMap),
        ))
