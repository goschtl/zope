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

Revision information:
$Id: Annotations.py,v 1.2 2002/06/10 23:27:51 jim Exp $
"""

from Interface.Verify import verifyObject
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations

class Annotations:
    """
    Test the IAnnotations interface.  Expects the IAnnotations
    to be in self.annotations
    """

    def setUp(self):
        self.obj = {1:2, 3:4}

    def testInterfaceVerifies(self):
        verifyObject(IAnnotations, self.annotations)

    def testStorage(self):
        """test __getitem__"""
        self.annotations['unittest'] = self.obj
        res = self.annotations['unittest']
        self.failUnlessEqual(self.obj, res)

    def testGetitemException(self):
        """test __getitem__ raises exception on unknown key"""
        self.assertRaises(KeyError, self.annotations.__getitem__,'randomkey')

    def testGet(self):
        """test get"""
        self.annotations['unittest'] = obj
        res = self.annotations.get('unittest')
        self.failUnlessEqual(obj, res)

    def testGet(self):
        """test get with no set"""
        res = self.annotations.get('randomkey')
        self.failUnlessEqual(None, res)

    def testGetDefault(self):
        """test get returns default"""
        res = self.annotations.get('randomkey', 'default')
        self.failUnlessEqual('default', res)

    def testDel(self):
        self.annotations['unittest'] = self.obj
        del self.annotations['unittest']
        self.failUnlessEqual(None, self.annotations.get('unittest'))

    def testDelRaisesKeyError(self):
        self.assertRaises(KeyError, self.annotations.__delitem__, 'unittest')
