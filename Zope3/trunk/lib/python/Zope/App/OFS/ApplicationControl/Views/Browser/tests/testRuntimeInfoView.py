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
##############################################################################

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.App.OFS.ApplicationControl.ApplicationControl import \
  applicationController
from Zope.App.OFS.ApplicationControl.IApplicationControl import \
  IApplicationControl
from Zope.App.OFS.ApplicationControl.IRuntimeInfo import IRuntimeInfo
from Zope.App.OFS.ApplicationControl.RuntimeInfo import RuntimeInfo
from Zope.App.OFS.ApplicationControl.Views.Browser.RuntimeInfoView \
  import RuntimeInfoView
from Zope.ComponentArchitecture import getService
from types import DictType
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup

class Test(PlacefulSetup, TestCase):

    def _TestView__newView(self, container):
        return RuntimeInfoView(container, None)

    def test_RuntimeInfoView(self):
        getService(None,'Adapters').provideAdapter(
              IApplicationControl, IRuntimeInfo, RuntimeInfo)
        test_runtimeinfoview = self._TestView__newView(applicationController)

        test_format = test_runtimeinfoview.runtimeInfo()
        self.failUnless(isinstance(test_format, DictType))

        assert_keys = ['ZopeVersion', 'PythonVersion', 'PythonPath',
              'SystemPlatform', 'CommandLine', 'ProcessId', 'Uptime' ]
        test_keys = test_format.keys()

        assert_keys.sort()
        test_keys.sort()
        self.failUnless(assert_keys == test_keys)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
