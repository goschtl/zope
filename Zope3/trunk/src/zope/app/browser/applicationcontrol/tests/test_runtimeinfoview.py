##############################################################################
#
# Copyright (c) 2001, 2002, 2003 Zope Corporation and Contributors.
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
"""Runtime View tests

$Id: test_runtimeinfoview.py,v 1.8 2003/11/21 17:11:53 jim Exp $
"""
import unittest
from types import DictType
from zope.app.tests import ztapi

from zope.app.applicationcontrol.applicationcontrol import applicationController
from zope.app.applicationcontrol.runtimeinfo import RuntimeInfo
from zope.app.browser.applicationcontrol.runtimeinfo import RuntimeInfoView
from zope.app.interfaces.applicationcontrol import \
     IApplicationControl, IRuntimeInfo
from zope.app.services.servicenames import Adapters
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getService

class Test(PlacefulSetup, unittest.TestCase):

    def _TestView__newView(self, container):
        view = RuntimeInfoView()
        view.context = container
        view.request = None
        return view

    def test_RuntimeInfoView(self):
        ztapi.provideAdapter(IApplicationControl, IRuntimeInfo, RuntimeInfo)
        test_runtimeinfoview = self._TestView__newView(applicationController)

        test_format = test_runtimeinfoview.runtimeInfo()
        self.failUnless(isinstance(test_format, DictType))

        assert_keys = ['ZopeVersion', 'PythonVersion', 'PythonPath',
              'SystemPlatform', 'CommandLine', 'ProcessId', 'Uptime' ]
        test_keys = test_format.keys()

        assert_keys.sort()
        test_keys.sort()
        self.failUnless(assert_keys == test_keys)

        self.failUnless(test_format["ZopeVersion"] != "N/A")

    def test_RuntimeInfoFailureView(self):
        test_runtimeinfoview = self._TestView__newView(applicationController)

        test_format = test_runtimeinfoview.runtimeInfo()
        self.failUnless(isinstance(test_format, DictType))

        assert_keys = ['ZopeVersion', 'PythonVersion', 'PythonPath',
              'SystemPlatform', 'CommandLine', 'ProcessId', 'Uptime', 'Hint']
        test_keys = test_format.keys()

        assert_keys.sort()
        test_keys.sort()
        self.failUnless(assert_keys == test_keys)

        self.failUnless(test_format["ZopeVersion"] == "N/A")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
