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
##############################################################################
"""

$Id: testApplicationControl.py,v 1.2 2002/06/10 23:27:54 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Interface.Verify import verifyObject

import time
from Zope.App.OFS.ApplicationControl.ApplicationControl import \
  ApplicationControl
from Zope.App.OFS.ApplicationControl.IApplicationControl import \
  IApplicationControl

# seconds, time values may differ in order to be assumed equal
time_tolerance = 2

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  Don't use this
# tests outside the Zope package.

# from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

#############################################################################

class Test(TestCase):

    def _Test__new(self):
        return ApplicationControl()

    ############################################################
    # Interface-driven tests:

    def test_IVerify(self):
        verifyObject(IApplicationControl, self._Test__new())

    def test_startTime(self):
        assert_time = time.time()
        test_time = self._Test__new().getStartTime()
        
        self.failUnless(abs(assert_time - test_time) < time_tolerance)

    def test_plugins(self):
        test_appctrl = self._Test__new()
        assert_info = ( {'name':'foo', 'title':'I\'m a lumberjack'},
                        {'name':'bar', 'title':'and i feel fine.'},
                        {'name':'nudges', 'title':'The nudge'},
                        {'name':'dash', 'title':'The dash'} )

        for info in assert_info:
            test_appctrl.registerView(info['name'], info['title'])

        test_info = test_appctrl.getListOfViews()
        self.failUnlessEqual(assert_info, test_info)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
