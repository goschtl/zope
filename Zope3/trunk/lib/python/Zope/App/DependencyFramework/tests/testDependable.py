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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testDependable.py,v 1.2 2002/11/18 22:25:17 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Annotation.AttributeAnnotations \
     import AttributeAnnotations
from Zope.App.tests.PlacelessSetup import PlacelessSetup
class C:pass

class Test(PlacelessSetup, TestCase):

    
    def _Test__new(self):
        from Zope.App.DependencyFramework.Dependable import Dependable
        return Dependable(AttributeAnnotations(C()))

    def testVerifyInterface(self):
        from Interface.Verify import verifyObject
        from Zope.App.DependencyFramework.IDependable import IDependable
        object = self._Test__new()
        verifyObject(IDependable, object)

    def test(self):
        dependable = self._Test__new()
        self.failIf(dependable.dependents())
        dependable.addDependent('/a/b')
        dependable.addDependent('/c/d')
        dependable.addDependent('/c/e')
        dependents = list(dependable.dependents())
        dependents.sort()
        self.assertEqual(dependents, ['/a/b', '/c/d', '/c/e'])
        dependable.removeDependent('/c/d')
        dependents = list(dependable.dependents())
        dependents.sort()
        self.assertEqual(dependents, ['/a/b', '/c/e'])
 
def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
