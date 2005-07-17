##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the unique id generation.

$Id$
"""

from unittest import TestCase, TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from Products.CMFCore.tests.base.testcase import SecurityTest

class UniqueIdGeneratorTests(SecurityTest):

    def setUp(self):
        from Products.CMFUid.UniqueIdGeneratorTool import UniqueIdGeneratorTool
        SecurityTest.setUp(self)
        self.root._setObject('portal_uidgenerator', UniqueIdGeneratorTool())
    
    def test_interface(self):
        from zope.interface.verify import verifyObject
        from Products.CMFUid.interfaces import IUniqueIdGenerator
        generator = self.root.portal_uidgenerator
        verifyObject(IUniqueIdGenerator, generator)
        
    def test_returnedUidsAreValidAndDifferent(self):
        generator = self.root.portal_uidgenerator
        uid1 = generator()
        uid2 = generator()
        self.failIfEqual(uid1, uid2)
        self.failIfEqual(uid1, None)
        
    def test_converter(self):
        generator = self.root.portal_uidgenerator
        uid = generator()
        str_uid = str(uid)
        result = generator.convert(str_uid)
        self.assertEqual(result, uid)

    def test_migrationFromBTreeLengthToInteger(self):
        from BTrees.Length import Length
        # For backwards compatibility with CMF 1.5.0 and 1.5.1, check if
        # the generator correctly replaces a ``BTree.Length.Length`` object
        # to an integer.
        generator = self.root.portal_uidgenerator
        uid1 = generator()
        generator._uid_counter = Length(uid1)
        self.failUnless(isinstance(generator._uid_counter, Length))
        uid2 = generator()
        self.failUnless(isinstance(generator._uid_counter, int))
        self.failIfEqual(uid1, uid2)

def test_suite():
    return TestSuite((
        makeSuite(UniqueIdGeneratorTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
