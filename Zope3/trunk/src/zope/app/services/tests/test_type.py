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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_type.py,v 1.1 2003/01/29 18:49:46 jim Exp $
"""

from unittest import TestSuite, makeSuite
from zope.interface.tests.test_type import TestTypeRegistry
from zope.app.services.type import PersistentTypeRegistry

class Test(TestTypeRegistry):

    def new_instance(self):
        return PersistentTypeRegistry()


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))
