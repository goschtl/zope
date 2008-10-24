##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""
Test setup for grok.admin.introspector.
"""
import os
import z3c.testsetup
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                            'ZopeIntrospectorUIFunctionalLayer',
                            allow_teardown=True)

# This we say: include all testfiles in or below the
# package in the tests.
#
test_suite = z3c.testsetup.register_all_tests('zope.introspectorui',
                                              layer = FunctionalLayer)
