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
  ApplicationController
from Zope.App.OFS.ApplicationControl.ServerControl.IServerControl import \
  IServerControl
from \
  Zope.App.OFS.ApplicationControl.ServerControl.Views.Browser.ServerControlView\
  import ServerControlView
from Zope.App.OFS.ApplicationControl.ServerControl.ServerControl import \
  ServerControl
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup

class Test(PlacefulSetup, TestCase):

    def _TestView__newView(self, container, request):
        return ServerControlView(container, request)

    def test_ServerControlView(self):
        getService(None,"Utilities").provideUtility(
              IServerControl, ServerControl())

        test_serverctrl = self._TestView__newView(
            ApplicationController,
            {'shutdown': 1},
            )
        test_serverctrl.action()

        test_serverctrl = self._TestView__newView(
            ApplicationController,
            {'restart': 1},
            )
        test_serverctrl.action()

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
