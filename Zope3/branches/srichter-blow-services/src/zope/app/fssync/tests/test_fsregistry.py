##############################################################################
#
# Copyright) 2001, 2002 Zope Corporation and Contributors.
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
"""Test FSRegistry File-system synchronization utilities

$Id$
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.testing.cleanup import CleanUp
from zope.interface.verify import verifyObject
from zope.exceptions import DuplicationError, NotFoundError

from zope.app.fssync.interfaces import IGlobalFSSyncUtility
from zope.app.fssync.tests.sampleclass \
     import C1, C2, CDirAdapter, CFileAdapter, CDefaultAdapter
from zope.app.fssync.fsregistry \
     import getSynchronizer, provideSynchronizer, fsRegistry

class Test(CleanUp, TestCase):
    """Test Interface for FSRegistry Instance.
    """

    def testInterfaceVerification(self):
        verifyObject(IGlobalFSSyncUtility, fsRegistry)

    def testFSRegistry(self):
        """ Test Class and Factory registration and getSynchronizer to get
           appropriate factory for that class.
        """
        self.assertRaises(NotFoundError, getSynchronizer, C1())

        provideSynchronizer(C1, CFileAdapter)
        cl = C1()
        fac = getSynchronizer(cl)
        self.assertEqual(fac.__class__, CFileAdapter)
        self.assertEqual(fac.getBody(), C1.__doc__)

        provideSynchronizer(C2, CDirAdapter)
        fac = getSynchronizer(C2())
        self.assertEqual(fac.__class__, CDirAdapter)
        self.assertEqual(fac.contents(), [])

    def testFSRegitryDefaultFactory(self):
        """Test for default Factory
        """
        provideSynchronizer(None, CDefaultAdapter)
        fac = getSynchronizer(C1())
        self.assertEqual(fac.__class__, CDefaultAdapter)

        fac = getSynchronizer(C2())
        self.assertEqual(fac.__class__, CDefaultAdapter)

    def testFSRegDuplication(self):
        """Test for duplication in registring the same class in
        to the Registry.
        """
        provideSynchronizer(C2, CFileAdapter)
        #Try to change the adapter for same class should
        #throw a duplication error
        self.assertRaises(DuplicationError,
                          provideSynchronizer, C2, CDirAdapter)

def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')
