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
"""NameRegistry tests

$Id: test_nameregistry.py,v 1.1 2003/06/21 21:22:13 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.app.services.registration import NameRegistry
from zope.app.services.registration import NameComponentRegistry
from zope.app.context import ContextWrapper
from zope.context import getWrapperContainer

class RegistrationStub:

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def getComponent(self):
        return self.component


class RegistryStub:

    def __init__(self, nonzero=0, active=None):
        self._nonzero = nonzero or (active and 1 or 0)
        self._active = active

    def __nonzero__(self):
        return self._nonzero

    def active(self):
        return self._active


class TestNameRegistry(TestCase):

    def setUp(self):
        self.container = object()
        self.subject = ContextWrapper(NameRegistry(), self.container)

    def test_queryRegistrationsFor(self):
        subject = self.subject
        cfg = RegistrationStub(name="Foo")
        self.assertEquals(subject.queryRegistrationsFor(cfg), None)
        self.assertEquals(subject.queryRegistrationsFor(cfg, 42), 42)

        registry = RegistryStub()
        subject._bindings["Foo"] = registry
        result = subject.queryRegistrationsFor(cfg)
        self.assertEquals(result, registry)
        self.assertEquals(getWrapperContainer(result), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(result)),
                          self.container)

    def test_queryRegistrations(self):
        subject = self.subject
        self.assertEquals(subject.queryRegistrations("Foo"), None)
        self.assertEquals(subject.queryRegistrations("Foo", 42), 42)

        registry = RegistryStub()
        subject._bindings["Foo"] = registry
        result = subject.queryRegistrations("Foo")
        self.assertEquals(result, registry)
        self.assertEquals(getWrapperContainer(result), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(result)),
                          self.container)

    def test_createRegistrationsFor(self):
        subject = self.subject
        cfg1 = RegistrationStub(name='Foo')
        cfg2 = RegistrationStub(name='Bar')
        r1 = subject.createRegistrationsFor(cfg1)
        r2 = subject.createRegistrationsFor(cfg2)
        r3 = subject.createRegistrationsFor(cfg1)
        self.assertEquals(r1, r3)
        self.assertNotEquals(r1, r2)
        self.assertNotEquals(r2, r3)
        self.assertEquals(r3, subject._bindings['Foo'])
        self.assertEquals(getWrapperContainer(r3), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(r3)),
                          self.container)
        self.failUnless(subject._p_changed)

    def test_createRegistrations(self):
        subject = self.subject
        r1 = subject.createRegistrations('Foo')
        r2 = subject.createRegistrations('Bar')
        r3 = subject.createRegistrations('Foo')
        self.assertEquals(r1, r3)
        self.assertNotEquals(r1, r2)
        self.assertNotEquals(r2, r3)
        self.assertEquals(r3, subject._bindings['Foo'])
        self.assertEquals(getWrapperContainer(r3), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(r3)),
                          self.container)
        self.failUnless(subject._p_changed)

    def test_listRegistrationNames(self):
        subject = self.subject
        self.assertEquals(tuple(subject.listRegistrationNames()), ())
        subject._bindings['Foo'] = 1
        self.assertEquals(tuple(subject.listRegistrationNames()), ('Foo',))
        subject._bindings['Bar'] = 0   # false values should be filtered out
        self.assertEquals(tuple(subject.listRegistrationNames()), ('Foo',))

class TestNameComponentRegistry(TestNameRegistry):

    def setUp(self):
        self.container = object()
        self.subject = ContextWrapper(NameComponentRegistry(),
                                      self.container)

    def test_queryActiveComponent(self):
        subject = self.subject
        self.assertEquals(subject.queryActiveComponent('xyzzy'), None)
        self.assertEquals(subject.queryActiveComponent('xyzzy', 'No'), 'No')
        subject._bindings['xyzzy'] = RegistryStub()
        self.assertEquals(subject.queryActiveComponent('xyzzy'), None)
        subject._bindings['xyzzy'] = RegistryStub(nonzero=1)
        self.assertEquals(subject.queryActiveComponent('xyzzy'), None)
        cfg = RegistrationStub(component='X')
        subject._bindings['xyzzy'] = RegistryStub(active=cfg)
        self.assertEquals(subject.queryActiveComponent('xyzzy'), 'X')


def test_suite():
    return TestSuite((
        makeSuite(TestNameRegistry),
        makeSuite(TestNameComponentRegistry),
        ))


if __name__=='__main__':
    main(defaultTest='test_suite')
