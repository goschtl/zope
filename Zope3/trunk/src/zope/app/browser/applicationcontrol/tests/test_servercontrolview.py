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

from zope.app.applicationcontrol.applicationcontrol import \
  applicationController
from zope.app.interfaces.applicationcontrol.servercontrol import \
  IServerControl
from zope.app.browser.applicationcontrol.servercontrol import ServerControlView
from zope.app.applicationcontrol.servercontrol import \
  ServerControl
from zope.component import getService
from zope.app.services.servicenames import Utilities
from zope.app.services.tests.placefulsetup\
           import PlacefulSetup

class Test(PlacefulSetup, TestCase):

    def _TestView__newView(self, container, request):
        return ServerControlView(container, request)

    def test_ServerControlView(self):
        getService(None,Utilities).provideUtility(
              IServerControl, ServerControl())

        test_serverctrl = self._TestView__newView(
            applicationController,
            {'shutdown': 1},
            )
        test_serverctrl.action()

        test_serverctrl = self._TestView__newView(
            applicationController,
            {'restart': 1},
            )
        test_serverctrl.action()

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
