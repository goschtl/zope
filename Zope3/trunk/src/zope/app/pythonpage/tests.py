##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for Python Page

$Id: tests.py,v 1.3 2004/03/02 15:50:04 srichter Exp $
"""
import unittest
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interpreter.interfaces import IInterpreter
from zope.app.interpreter.python import PythonInterpreter
from zope.app.location import LocationPhysicallyLocatable
from zope.app.tests import placelesssetup, ztapi
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.component.servicenames import Utilities
from zope.interface import implements
from zope.testing.doctestunit import DocTestSuite


class Root(Contained):
    implements(IContainmentRoot)    

    __parent__ = None
    __name__ = 'root'

def setUp():
    placelesssetup.setUp()
    service = zapi.getService(None, Utilities)
    service.provideUtility(IInterpreter, PythonInterpreter,
                             'text/server-python')

    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)
    ztapi.provideAdapter(IContainmentRoot, IPhysicallyLocatable,
                         RootPhysicallyLocatable)
    

def tearDown():
    placelesssetup.tearDown()

    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.pythonpage', setUp, tearDown),
        ))

if __name__ == '__main__':
    unittest.main()
