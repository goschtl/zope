##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: BaseTestIDependable.py,v 1.1 2002/10/14 11:51:05 jim Exp $
"""

class BaseTestIDependable:
    """Test whether objects implement IDependable
    """

    def _Test__new(self):
        raise TypeError, "Sub-classes must implement _Test__new."

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
        
    

__doc__ = BaseTestIDependable.__doc__ + __doc__

