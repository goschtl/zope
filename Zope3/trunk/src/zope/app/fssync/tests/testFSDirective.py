##############################################################################
#
# Copyright) 2001, 2002 Zope Corporation and Contributors.
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
"""Test FSRegistry File-system synchronization services

$Id: testFSDirective.py,v 1.2 2003/05/05 18:01:02 gvanrossum Exp $
"""

from cStringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite

from zope.configuration.xmlconfig import testxmlconfig as xmlconfig, XMLConfig
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
from zope.app.fssync.fsregistry import getSynchronizer
from zope.app.interfaces.fssync \
     import IGlobalFSSyncService, IObjectFile, IObjectDirectory
from zope.interface.verify import verifyObject
from zope.exceptions import DuplicationError, NotFoundError
from zope.configuration.exceptions import ConfigurationError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.service import UndefinedService
from zope.app.fssync.tests.sampleclass \
     import C1, C2, CDirAdapter, CFileAdapter, CDefaultAdapter

import zope.app.fssync

template = """
   <zopeConfigure xmlns="http://namespaces.zope.org/zope"
   xmlns:fssync="http://namespaces.zope.org/fssync">
   %s
   </zopeConfigure>"""

class Test(PlacelessSetup, TestCase):
    """
    """    
    def setUp(self):
        PlacelessSetup.setUp(self)
        XMLConfig('meta.zcml', zope.app.fssync)()

    def testFSDirective(self):
        """Test for Synchrozier not found and Registering the
        adapter for a class.
        """
        from zope.app.fssync.tests.sampleclass import C1
    
        # Register the adapter for the class
        self.assertRaises(NotFoundError, getSynchronizer, C2())

        xmlconfig(StringIO(template % (
             """
             <fssync:adapter
             class_="zope.app.fssync.tests.sampleclass.C2"
             factory="zope.app.fssync.tests.sampleclass.CDirAdapter"
             />
             """
             )))
        self.assertEqual(getSynchronizer(C2()).__class__, CDirAdapter)

    def testFSDirectiveDefaultAdapter(self):
        """Test for getting default adapter for not registered Classes"""
        xmlconfig(StringIO(template % (
              """
              <fssync:adapter
              factory = "zope.app.fssync.tests.sampleclass.CDefaultAdapter"
              />
              """
              )))
        self.assertEqual(getSynchronizer(C2()).__class__, CDefaultAdapter)
        
    def testFSDirectiveDuplicate(self):
        """Duplication test"""
        xmlconfig(StringIO(template % (
             """
             <fssync:adapter
             class_="zope.app.fssync.tests.sampleclass.C1"
             factory="zope.app.fssync.tests.sampleclass.CDirAdapter"
             />
             """
             )))
        
        self.assertRaises(DuplicationError, xmlconfig, StringIO(template % (
             """
             <fssync:adapter
             class_="zope.app.fssync.tests.sampleclass.C1"
             factory="zope.app.fssync.tests.sampleclass.CFileAdapter"
             />
             """
             )))

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
