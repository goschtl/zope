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

$Id: tests.py,v 1.2 2004/02/24 16:50:28 philikon Exp $
"""
import unittest
from zope.app import zapi
from zope.app.container.contained import Contained
from zope.app.interfaces.interpreter import IInterpreter, IInterpreterService
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interpreter import interpreterService
from zope.app.interpreter.python import PythonInterpreter
from zope.app.location import LocationPhysicallyLocatable
from zope.app.tests import placelesssetup, ztapi
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.component.servicenames import Services
from zope.interface import implements
from zope.testing.doctestunit import DocTestSuite


class Root(Contained):
    implements(IContainmentRoot)    

    __parent__ = None
    __name__ = 'root'

def setUp():
    placelesssetup.setUp()
    interpreterService.provideInterpreter('text/server-python',
                                          PythonInterpreter)
    services = zapi.getService(None, Services)
    services.defineService('Interpreter', IInterpreterService)
    services.provideService('Interpreter', interpreterService)

    ztapi.provideAdapter(None, IPhysicallyLocatable,
                         LocationPhysicallyLocatable)
    ztapi.provideAdapter(IContainmentRoot, IPhysicallyLocatable,
                         RootPhysicallyLocatable)
    

def tearDown():
    placelesssetup.tearDown()

    
def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.pythonpage'),
        ))

if __name__ == '__main__':
    unittest.main()
