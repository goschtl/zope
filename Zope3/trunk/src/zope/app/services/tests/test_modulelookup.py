##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Local module lookup tests

Note that when we get around to implementing module services, those
tests will go here too.

$Id: test_modulelookup.py,v 1.5 2004/01/13 14:27:56 fdrake Exp $
"""

from zope.testing.doctestunit import DocTestSuite

from zope.app.services.registration import RegistrationManagerContainer
from zope.app.interfaces.services.module import IModuleManager
from zope.interface import implements
from zope.app.container.contained import Contained, setitem
from zope.app.tests.placelesssetup import setUp, tearDown

class MyModuleManager(object):
    implements(IModuleManager)
    
    def __init__(self, module):
        self.module = module

    def getModule(self):
        return self.module

class MyFolder(RegistrationManagerContainer, dict, Contained):
    def __setitem__(self, name, object):
        setitem(self, super(MyFolder, self).__setitem__, name, object)


def test_findMoule():
    """
    Tests for RegistrationManagerContainer.findModule().

    >>> folder = MyFolder()
    >>> folder['m1.py'] = MyModuleManager(1)
    >>> folder['m1'] = MyModuleManager(0)
    >>> folder['m2'] = MyModuleManager(2)
    >>> next = MyFolder()
    >>> next['m3'] = MyModuleManager(3)
    >>> next['z.y.m4'] = MyModuleManager(4)
    >>> folder.__parent__ = next

    >>> folder.findModule('m1')
    1
    >>> folder.findModule('m2')
    2
    >>> folder.findModule('m3')
    3
    >>> folder.findModule('z.y.m4')
    4
    >>> folder.findModule('m5')
    Traceback (most recent call last):
    ...
    ImportError: m5

    >>> import zope.app.services.tests.test_modulelookup
    >>> m = folder.findModule('zope.app.services.tests.test_modulelookup')
    >>> int(m is zope.app.services.tests.test_modulelookup)
    1
    
    """

def test_resolve():
    """
    >>> folder = MyFolder()
    >>> import zope.app.services.tests.test_modulelookup
    >>> f = folder.resolve(
    ...    'zope.app.services.tests.test_modulelookup.test_resolve')
    >>> int(f is zope.app.services.tests.test_modulelookup.test_resolve)
    1
    """

def test_suite():
    return DocTestSuite(setUp=setUp, tearDown=tearDown)

if __name__ == '__main__': unittest.main()
