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
"""

$Id: testContents.py,v 1.3 2002/06/13 23:15:43 jim Exp $
"""

import unittest

from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.Views.Browser.Contents \
     import ServiceManagerContents
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Container.Views.Browser.tests.testContents \
     import BaseTestContentsBrowserView
from Zope.Publisher.Browser.BrowserRequest import TestRequest

class IDummy(Interface):
    pass

class Dummy:
    __implements__ = IDummy


    
class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        return ServiceManager()

    def _TestView__newView(self, container):
        from Zope.Publisher.Browser.BrowserRequest import TestRequest
        return ServiceManagerContents(container, TestRequest())

    def testExtractContents(self):
        """ Does _extractContents return the correct information? """

        smc = ServiceManagerContents(None , TestRequest())
        info = smc._extractContentInfo(('dummy', Dummy(),))

        self.assert_('IDummy' in info['interfaces'])

    def testInfo(self):
        """ Do we get the correct information back from
            ServiceManagerContents?
        """

        sm = ServiceManager()
        dummy = Dummy()
        sm.setObject('dummy', dummy)

        smc = ServiceManagerContents(sm, TestRequest())
        info_list = smc.listContentInfo()

        self.assertEquals(len(info_list), 1)

        interfaces = [ x['interfaces'] for x in info_list ]
        self.assert_('IDummy' in interfaces[0])

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.main()
