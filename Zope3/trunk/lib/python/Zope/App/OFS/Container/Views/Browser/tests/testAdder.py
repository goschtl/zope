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
"""test Adding

test Adding for interface compliance

$Id: testAdder.py,v 1.2 2002/06/20 20:00:21 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import \
     PlacefulSetup
from Zope.App.OFS.Container.Views.Browser.Adding import Adding
from Zope.ComponentArchitecture.tests.Request import Request

class Test(PlacefulSetup, TestCase):
    def testAdd(self):
        ""

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
