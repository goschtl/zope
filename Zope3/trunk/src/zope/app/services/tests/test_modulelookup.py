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

$Id: test_modulelookup.py,v 1.3 2003/07/03 15:42:48 srichter Exp $
"""

from zope.testing.doctestunit import DocTestSuite
from zope.context import Wrapper

from zope.app.services.registration import RegistrationManagerContainer
from zope.app.interfaces.services.module import IModuleManager
from zope.interface import implements


class MyModuleManager(object):
    implements(IModuleManager)
    
    def __init__(self, module):
        self.module = module

    def getModule(self):
        return self.module

class MyFolder(RegistrationManagerContainer, dict):
    def setObject(self, name, object):
        self[name] = object
        return name


def test_findMoule():
    """

    >>> folder = MyFolder()
    >>> folder['m1.py'] = MyModuleManager(1)
    >>> folder['m1'] = MyModuleManager(0)
    >>> folder['m2'] = MyModuleManager(2)
    >>> next = MyFolder()
    >>> next['m3'] = MyModuleManager(3)
    >>> next['z.y.m4'] = MyModuleManager(4)
    >>> folder = Wrapper(folder, next)

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

def test_suite(): return DocTestSuite()
if __name__ == '__main__': unittest.main()
