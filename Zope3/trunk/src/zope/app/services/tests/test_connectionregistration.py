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
"""Unit test for ConnectionRegistration.

$Id: test_connectionregistration.py,v 1.1 2003/06/21 21:22:13 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, main, makeSuite
from zope.app.services.connection import ConnectionRegistration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.services.registration import IRegistry
from zope.app.services.registration import RegistrationStack
from zope.context import ContextMethod
from zope.app.context import ContextWrapper
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.registration import IAttributeRegisterable
from zope.app.tests import setup
from zope.app.interfaces.services.service import ILocalService
from zope.interface import implements

class DependableStub:

    implements(IDependable)

    def addDependent(self, location):
        pass

    def removeDependent(self, location):
        pass

    def dependents(self):
        pass


class TestDA(DependableStub):

    implements(IZopeDatabaseAdapter, IDependable, IRegistered)

    def addUsage(self, location):
        pass


class ConnectionServiceStub(DependableStub):

    implements(IConnectionService, IRegistry, IDependable,
               IAttributeRegisterable, ILocalService)

    def __init__(self):
        self.bindings = {}

    def queryRegistrationsFor(self, cfg, default=None):
        return self.queryRegistrations(cfg.name)
    queryRegistrationsFor = ContextMethod(queryRegistrationsFor)

    def queryRegistrations(self, name, default=None):
        registry = self.bindings.get(name, default)
        return ContextWrapper(registry, self)
    queryRegistrations = ContextMethod(queryRegistrations)

    def createRegistrationsFor(self, cfg):
        return self.createRegistrations(cfg.name)
    createRegistrationsFor = ContextMethod(createRegistrationsFor)

    def createRegistrations(self, name):
        try:
            registry = self.bindings[name]
        except KeyError:
            self.bindings[name] = registry = RegistrationStack()
        return ContextWrapper(registry, self)
    createRegistrations = ContextMethod(createRegistrations)


class TestConnectionRegistration(PlacefulSetup, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        self.service = setup.addService(sm, 'SQLDatabaseConnections',
                                        ConnectionServiceStub())

        self.default = traverse(self.rootFolder,
                           '++etc++site/default')
        self.default.setObject('da', TestDA())
        self.da = traverse(self.default, 'da')

        self.cm = self.default.getRegistrationManager()
        key = self.cm.setObject('',
                  ConnectionRegistration('conn_name',
                                          '/++etc++site/default/da'))
        self.config = traverse(self.default.getRegistrationManager(), key)

    def tearDown(self):
        PlacefulSetup.tearDown(self)

    def test_getComponent(self):
        # This should be already tested by ComponentRegistration tests, but
        # let's doublecheck
        self.assertEqual(self.config.getComponent(), self.da)

    def test_status(self):
        self.assertEqual(self.config.status, UnregisteredStatus)
        self.config.status = ActiveStatus
        self.assertEqual(self.config.status, ActiveStatus)
        cr = self.service.queryRegistrations('conn_name')
        self.assertEqual(cr.active(), self.config)


def test_suite():
    return makeSuite(TestConnectionRegistration)


if __name__=='__main__':
    main(defaultTest='test_suite')
