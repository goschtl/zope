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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_registrationstatusproperty.py,v 1.3 2003/09/02 20:46:51 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.component.interfaces import IServiceService
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.tests.registrationstack import TestingRegistration
from zope.app.services.tests.registrationstack import TestingRegistrationStack
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.context import ContextWrapper
from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.services.registration import NoLocalServiceError
from zope.interface import implements


class TestingRegistration(TestingRegistration):
    serviceType = "Services"
    service_type = "Test"

class PassiveRegistration(TestingRegistration):
    serviceType = "NoSuchService"

class UtilityRegistration(TestingRegistration):
    serviceType = "Utilities"

class TestingRegistrationStack(TestingRegistrationStack):
    class_ = TestingRegistration

class TestingServiceManager:

    implements(IServiceService) # I lied

    registry = None

    def getService(self, name):
        if name in ("Services", "Utilities"):
            return self
        raise ComponentLookupError("Wrong service name", name)

    def queryService(self, name, default=None):
        if name in ("Services", "Utilities"):
            return self
        else:
            return default

    def queryLocalService(self, name, default=None):
        if name == "Services":
            return self
        else:
            return default

    def queryRegistrationsFor(self, registration, default=None):
        if registration.service_type != "Test":
            raise ValueError("Bad service type", registration.service_type)
        return self.registry

    def createRegistrationsFor(self, registration):
        if registration.service_type != "Test":
            raise ValueError("Bad service type", registration.service_type)
        self.registry = TestingRegistrationStack()
        return self.registry


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, folders=True)
        self.__sm = TestingServiceManager()
        self.rootFolder.setSiteManager(self.__sm)

    def test_property(self):

        configa = ContextWrapper(TestingRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        configa.status = RegisteredStatus
        self.assertEqual(self.__sm.registry._data, (None, 'a'))
        self.assertEqual(configa.status, RegisteredStatus)

        configa.status = ActiveStatus
        self.assertEqual(self.__sm.registry._data, ('a', ))
        self.assertEqual(configa.status, ActiveStatus)

        configb = ContextWrapper(TestingRegistration('b'), self.rootFolder)
        self.assertEqual(self.__sm.registry._data, ('a', ))
        self.assertEqual(configb.status, UnregisteredStatus)

        configb.status = RegisteredStatus
        self.assertEqual(self.__sm.registry._data, ('a', 'b'))
        self.assertEqual(configb.status, RegisteredStatus)

        configc = ContextWrapper(TestingRegistration('c'), self.rootFolder)
        self.assertEqual(configc.status, UnregisteredStatus)
        self.assertEqual(self.__sm.registry._data, ('a', 'b'))

        configc.status = RegisteredStatus
        self.assertEqual(self.__sm.registry._data, ('a', 'b', 'c'))
        self.assertEqual(configc.status, RegisteredStatus)

        configc.status = ActiveStatus
        self.assertEqual(self.__sm.registry._data, ('c', 'a', 'b'))
        self.assertEqual(configc.status, ActiveStatus)

        configc.status = UnregisteredStatus
        self.assertEqual(self.__sm.registry._data, (None, 'a', 'b'))
        self.assertEqual(configc.status, UnregisteredStatus)
        self.assertEqual(configb.status, RegisteredStatus)
        self.assertEqual(configa.status, RegisteredStatus)

    def test_passive(self):
        # scenario:
        #   1. create and configure an SQLConnectionService
        #   2. create and configure a database adapter&connection
        #   3. disable SQLConnectionService
        # now the ConnectionRegistration.status cannot access the
        # SQLConnectionService

        configa = ContextWrapper(PassiveRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        try:
            configa.status = RegisteredStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")

        try:
            configa.status = ActiveStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")


        # we should also get an error if there *is a matching service,
        # not it is non-local

        configa = ContextWrapper(UtilityRegistration('a'), self.rootFolder)
        self.assertEqual(configa.status, UnregisteredStatus)

        try:
            configa.status = RegisteredStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")

        try:
            configa.status = ActiveStatus
        except NoLocalServiceError:
            self.assertEqual(configa.status, UnregisteredStatus)
        else:
            self.fail("should complain about missing service")


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
