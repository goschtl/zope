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
"""NameConfigurable tests

$Id: testNameConfigurable.py,v 1.2 2002/12/12 11:32:34 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.App.OFS.Services.Configuration import NameConfigurable
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Proxy.ContextWrapper import getWrapperContainer
from Zope.Proxy.ContextWrapper import getWrapperContext


class ConfigurationStub:

    def __init__(self, **kw):
        self.__dict__.update(kw)

class RegistryStub:

    pass


class TestNameConfigurable(TestCase):

    def setUp(self):
        self.container = object()
        self.subject = ContextWrapper(NameConfigurable(), self.container)

    def test_queryConfigurationsFor(self):
        subject = self.subject
        cfg = ConfigurationStub(name="Foo")
        self.assertEquals(subject.queryConfigurationsFor(cfg), None)
        self.assertEquals(subject.queryConfigurationsFor(cfg, 42), 42)

        registry = RegistryStub()
        subject._bindings["Foo"] = registry
        result = subject.queryConfigurationsFor(cfg)
        self.assertEquals(result, registry)
        self.assertEquals(getWrapperContainer(result), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(result)),
                          self.container)

    def test_queryConfigurations(self):
        subject = self.subject
        self.assertEquals(subject.queryConfigurations("Foo"), None)
        self.assertEquals(subject.queryConfigurations("Foo", 42), 42)

        registry = RegistryStub()
        subject._bindings["Foo"] = registry
        result = subject.queryConfigurations("Foo")
        self.assertEquals(result, registry)
        self.assertEquals(getWrapperContainer(result), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(result)),
                          self.container)

    def test_createConfigurationsFor(self):
        subject = self.subject
        cfg1 = ConfigurationStub(name='Foo')
        cfg2 = ConfigurationStub(name='Bar')
        r1 = subject.createConfigurationsFor(cfg1)
        r2 = subject.createConfigurationsFor(cfg2)
        r3 = subject.createConfigurationsFor(cfg1)
        self.assertEquals(r1, r3)
        self.assertNotEquals(r1, r2)
        self.assertNotEquals(r2, r3)
        self.assertEquals(r3, subject._bindings['Foo'])
        self.assertEquals(getWrapperContainer(r3), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(r3)),
                          self.container)
        self.failUnless(subject._p_changed)

    def test_createConfigurations(self):
        subject = self.subject
        r1 = subject.createConfigurations('Foo')
        r2 = subject.createConfigurations('Bar')
        r3 = subject.createConfigurations('Foo')
        self.assertEquals(r1, r3)
        self.assertNotEquals(r1, r2)
        self.assertNotEquals(r2, r3)
        self.assertEquals(r3, subject._bindings['Foo'])
        self.assertEquals(getWrapperContainer(r3), subject)
        self.assertEquals(getWrapperContainer(getWrapperContainer(r3)),
                          self.container)
        self.failUnless(subject._p_changed)

    def test_listConfigurationNames(self):
        subject = self.subject
        self.assertEquals(tuple(subject.listConfigurationNames()), ())
        subject._bindings['Foo'] = 1
        self.assertEquals(tuple(subject.listConfigurationNames()), ('Foo',))
        subject._bindings['Bar'] = 0   # false values should be filtered out
        self.assertEquals(tuple(subject.listConfigurationNames()), ('Foo',))


def test_suite():
    return TestSuite((
        makeSuite(TestNameConfigurable),
        ))


if __name__=='__main__':
    main(defaultTest='test_suite')
