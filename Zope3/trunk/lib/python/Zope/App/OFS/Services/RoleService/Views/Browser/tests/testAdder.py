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
$Id: testAdder.py,v 1.2 2002/06/10 23:28:12 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture import getService
from Zope.ComponentArchitecture.IFactory import IFactory
from Zope.App.OFS.Container.Exceptions import DuplicateIDError
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import PlacefulSetup

class Role(object):
    __class_implements__ = IFactory

    def setId(self, id):
        self.id = id


    def getInterfaces():
        """Dummy stub."""
        pass

    def __call__():
        """A factory should always be callable."""
        pass


class Test(PlacefulSetup, TestCase):
    """Base adding tests

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.

    Subclasses need to define a method, '_TestAdderView__registry', that
    returns the appropriate registry.

    """

    def setUp(self):
        PlacefulSetup.setUp(self)
        getService(None,'Factories').provideFactory(
             "Zope.App.OFS.Services.RoleService.Role.", Role)

    def _TestView__newContext(self):
        from Zope.App.OFS.Services.RoleService.RoleService import RoleService
        return RoleService()

    def _TestView__newView(self, container):
        from Zope.App.OFS.Services.RoleService.Views.Browser.Adder import Adder 
        return Adder(container, None)


    def testAdding(self):
        """
            Does addition of a new object with the same ID as an existing
            object fail?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView( container )
        fa.action(id='foo' )

        self.assertEquals(len(container.keys()), 1)
        self.assertEquals(container.keys()[0], 'foo')
        self.assertEquals(len(container.values()), 1)
        self.assertEquals(container.values()[0].__class__, Role)

    def testDuplicates( self ):
        """
            Does addition of a new object with the same ID as an existing
            object fail?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        fa.action(id='foo')

        self.assertRaises(DuplicateIDError, fa.action, id='foo')

def test_suite():
    return TestSuite([makeSuite(Test)])

if __name__=='__main__':
    main(defaultTest='test_suite')
