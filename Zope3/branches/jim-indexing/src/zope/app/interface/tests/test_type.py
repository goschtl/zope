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
"""Persistent Type Registry Tests

$Id$
"""

from unittest import TestSuite, makeSuite
from zope.interface.tests.test_type import TestTypeRegistry
from zope.app.interface.type import PersistentTypeRegistry

class Test(TestTypeRegistry):

    def new_instance(self):
        return PersistentTypeRegistry()


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))
