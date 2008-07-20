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
import grokui.introspector
from zope.app.testing.functional import ZCMLLayer
from grok.testing import register_all_tests
from grok.ftests.test_grok_functional import GrokFunctionalLayer

ftesting_zcml = os.path.join(
    os.path.dirname(grokui.introspector.__file__), 'ftesting.zcml')

FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                            'GrokUIIntrospectorFunctionalLayer',
                            allow_teardown=True)

# This we say: include all testfiles in or below the
# grok.admin.introspector package in the tests.
#
test_suite = register_all_tests('grokui.introspector',
                                layer=FunctionalLayer)
