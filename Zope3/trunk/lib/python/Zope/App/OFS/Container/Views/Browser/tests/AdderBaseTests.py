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
from Zope.App.OFS.Container.Views.Browser.Adder import DuplicateIDError
from Zope.App.ZMI import provideClass
from Zope.App.OFS.Services.AddableService.tests.AddableSetup import AddableSetup
import Zope.Configuration.name
from Zope.ComponentArchitecture import getService, ComponentLookupError

class Foo: pass
class Bar: pass
class Baz: pass

AddPermission = 'add'

class BaseRegistryTest:
    """Base adder registry interaction tests.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.

    Subclasses need to define a method, '_TestAdderView__registry', that
    returns the appropriate registry.

    """
    
    def testNonesuch(self):
        """
            Do we get the correct information back when no
            addables have been registered?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        info_list = fa.listAddableInfo()
        self.failIf(info_list)

    def testHaveSome(self):
        """
            Do we get the correct information back when no
            addables have been registered?
        """
        data = [ ('foo', 'Foo', 'Foo Thingies')
               , ('bar', 'Bar', 'Barflies')
               , ('baz', 'Baz', 'Bazzing Around')
               ]

        addables = self._TestAdderView__registry()
        from Zope.ComponentArchitecture.tests.TestFactory import ClassFactoryWrapper
        for datum in data:
            apply(getService(None,addables).provideAddable, datum, {})
            getService(None,"Factories").provideFactory(datum[0], ClassFactoryWrapper(Foo))
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        info_list = fa.listAddableInfo()
        self.assertEquals(len(info_list), len(data))

        id_list = map(lambda x: x.id, info_list)
        self.assert_('foo' in id_list)
        self.assert_('bar' in id_list)
        self.assert_('baz' in id_list)

        title_list = map(lambda x: x.title, info_list)
        self.assert_('Foo' in title_list)
        self.assert_('Bar' in title_list)
        self.assert_('Baz' in title_list)

    def testNonesuchAction(self):
        """
            Can we get add an object back when no classes have
            been registered?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        self.assertRaises(ComponentLookupError, fa.action, type_name='foo', id='foo_123')

    def testHaveSomeAction(self):
        """
            Can we get add an object back when some classes have
            been registered?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        provideClass(self._TestAdderView__registry(),
                     qualified_name='Zope.App.OFS.tests.testContainerAdd.Foo',
                     _class=Foo,
                     permission=AddPermission,
                     title='Foo'
                    )
        provideClass(self._TestAdderView__registry(),
                     qualified_name='Zope.App.OFS.tests.testContainerAdd.Bar',
                     _class=Bar,
                     permission=AddPermission,
                     title='Bar'
                    )
        provideClass(self._TestAdderView__registry(),
                     qualified_name='Zope.App.OFS.tests.testContainerAdd.Baz',
                     _class=Baz,
                     permission=AddPermission,
                     title='Baz',
                    )

        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        info_list = fa.listAddableInfo()
        self.assertEquals(len(info_list), 3)

class BaseAddingTest:
    """Base adding tests

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.

    Subclasses need to define a method, '_TestAdderView__registry', that
    returns the appropriate registry.

    """

    def setUp(self):
        container = self._TestView__newContext()        
        provideClass(self._TestAdderView__registry(),
                     qualified_name='Zope.App.OFS.Container',
                     _class=container.__class__,
                     permission=AddPermission,
                     title='Container',
                    )

    def testAdding(self):
        """
            Does addition of a new object with the same ID as an existing
            object fail?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        fa.action(type_name='Zope.App.OFS.Container', id='foo')

        self.assertEquals(len(container.keys()), 1)
        self.assertEquals(container.keys()[0], 'foo')
        self.assertEquals(len(container.values()), 1)
        self.assertEquals(container.values()[0].__class__,
                           container.__class__)

    def testDuplicates(self):
        """
            Does addition of a new object with the same ID as an existing
            object fail?
        """
        container = self._TestView__newContext()
        fa = self._TestView__newView(container)
        fa.action(type_name='Zope.App.OFS.Container', id='foo')

        self.assertRaises(DuplicateIDError
                         , fa.action
                         ,  type_name='Zope.App.OFS.Container'
                         , id='foo'
                         )
