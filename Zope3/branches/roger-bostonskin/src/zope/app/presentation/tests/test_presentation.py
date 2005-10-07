##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the presentation module

$Id$
"""
import unittest

import zope.interface
from zope.component.exceptions import ComponentLookupError
from zope.configuration.exceptions import ConfigurationError
from zope.interface.verify import verifyObject
from zope.proxy import removeAllProxies
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.testing.doctestunit import DocTestSuite

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.interfaces.registration import IRegistered
from zope.app.component.testing import PlacefulSetup
from zope.app.container.contained import contained, uncontained, setitem
from zope.app.container.interfaces import IContained, ILocation
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.dependable import Dependable
from zope.app.dependable.interfaces import IDependable
from zope.app.folder import rootFolder
from zope.app.module import resolve
from zope.app.module.manager import ModuleManager
from zope.app.module.interfaces import IModuleManager
from zope.app.presentation.interfaces import IPageRegistration
from zope.app.presentation.interfaces import IZPTTemplate
from zope.app.presentation.registration import PageRegistration
from zope.app.presentation.registration import BoundTemplate
from zope.app.presentation.registration import PageRegistrationAddSubscriber
from zope.app.presentation.registration import PageRegistrationRemoveSubscriber
from zope.app.testing import ztapi, setup
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.app.traversing.api import traverse
from zope.app.traversing.interfaces import IPhysicallyLocatable


class I1(zope.interface.Interface):
    pass

class I1E(I1):
    pass

I2 = IBrowserRequest

class I3(zope.interface.Interface):
    pass

class I4(zope.interface.Interface):
    pass


class Registration(object):
    required = I1
    requestType = I2
    name = 'test'
    layer = 'default'
    provided = zope.interface.Interface

    with = property(lambda self: (self.requestType, ))
    factories = property(lambda self: (self.factory, ))

    def __repr__(self):
        return 'Registration(%s)' % self.factory.__name__

class C(object): pass

class PhonyTemplate(object):
    __name__ = __parent__ = None
    zope.interface.implements(IZPTTemplate, IDependable, IRegistered)

    _dependents = ()

    def addDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            +
            [location]
            )

    def removeDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            )

    def dependents(self):
        return self._dependents


source = '''
from zope.app.presentation.tests.test_presentation import PhonyTemplate

class A(object):
    def __init__(self, object, request):
        self.context = object
        self.request = request

    run = PhonyTemplate()
'''

class PhonyPathAdapter(object):
    zope.interface.implements(IPhysicallyLocatable)

    def __init__(self, context):
        self.context = context

    def getPath(self):
        return self.context.__name__

    def getRoot(self):
        root = self.context
        while root.__parent__ is not None:
            root = root.__parent__
        return root


class Folder(object):

    zope.interface.implements(IContained)

    __parent__ = __name__ = None

    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, ob):
        setitem(self, self.__setitem, key, ob)
    
    def __setitem(self, key, ob):
        self._dict[key] = ob

    def get(self, key, default=None):
        return self._dict.get(key, default)


class TestPageRegistration(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.rootFolder = rootFolder()
        setup.createSiteManager(self.rootFolder)
        default = self.rootFolder.getSiteManager()['default']
        self.__template = PhonyTemplate()
        default['t'] = self.__template
        ztapi.provideUtility(IModuleManager, ModuleManager(source), 'Foo.Bar')
        folder = contained(Folder(), self.rootFolder)
        self.folder = contained(Folder(), folder)

    def test_factories_template(self):
        registration = contained(
            PageRegistration('test', I1, 'zope.View',
                              "Foo.Bar.A",
                              template=self.__template,
                              ),
            self.folder,
            )

        c = C()
        request = TestRequest()
        factory = registration.component
        view = factory(c, request)
        self.assertEqual(view.__class__, BoundTemplate)
        self.assertEqual(removeAllProxies(view).template, self.__template)

        view = removeAllProxies(view).view
        self.assert_(issubclass(view.__class__, resolve('Foo.Bar.A')))
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(registration.required, I1)
        self.assertEqual(registration.requestType, I2)

    def test_factories_attribute(self):
        registration = contained(
            PageRegistration(
                I1, 'test', 'zope.View', "Foo.Bar.A", attribute='run'),
            self.folder,6
            )
        c = C()
        request = TestRequest()
        factory = registration.component
        view = factory(c, request)
        self.assertEquals(view, resolve('Foo.Bar.A').run)

    def test_factories_errors(self):
        registration = contained(
            PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A"),
            self.folder,
            )
        c = C()
        request = TestRequest()
        self.assertRaises(ConfigurationError, lambda: registration.component)
        registration.template = self.__template
        registration.attribute = 'run'
        self.assertRaises(ConfigurationError, lambda: registration.component)

    def test_registerAddSubscriber_template(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        ztapi.subscribe((IPageRegistration, IObjectAddedEvent), None,
                        PageRegistrationAddSubscriber)
        registration = PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A",
                                        template=self.__template)
        
        # Test add event
        self.folder['test'] = registration
        dependents = IDependable(self.__template)
        self.assert_('test' in dependents.dependents())

    def test_registerRemoveSubscriber_template(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        ztapi.subscribe((IPageRegistration, IObjectRemovedEvent), None,
                        PageRegistrationRemoveSubscriber)
        registration = PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A",
                                        template=self.__template)

        # Test remove event
        self.folder['test'] = registration
        uncontained(registration, self.folder, 'test')
        dependents = IDependable(self.__template)
        self.assert_('test' not in dependents.dependents())
        
    def test_addremoveNotify_attribute(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        registration = PageRegistration(I1, 'test', 'zope.View',
                                        "Foo.Bar.A", attribute='run')
        # Just add and remove registration to see that no errors occur
        self.folder['test'] = registration
        uncontained(registration, self.folder, 'test')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPageRegistration),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


