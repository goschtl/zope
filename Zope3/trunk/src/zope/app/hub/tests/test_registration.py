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
##############################################################################
"""
$Id: test_registration.py,v 1.3 2004/03/13 23:55:02 srichter Exp $
"""
from unittest import makeSuite, main, TestCase

from zope.app import zapi
from zope.app.hub import Registration
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse, canonicalPath
from zope.app.container.contained import ObjectAddedEvent
from zope.component import getService
from zope.app.servicenames import EventPublication, HubIds

class TestRegistration(PlacefulSetup, TestCase):
    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.createStandardServices()
        r = Registration()
        default = traverse(self.rootFolder, '++etc++site/default')
        default['registrar'] = r
        self.registrar = traverse(default, 'registrar')
        self.hub = getService(self.rootFolder, HubIds)
        self.events = getService(self.rootFolder, EventPublication)

    def testSubscribeUnsubscribe(self):
        r = self.registrar
        self.assertEqual(r.isSubscribed(), False)
        r.subscribe()
        self.assertEqual(r.isSubscribed(), True)
        self.assertRaises(RuntimeError, r.subscribe)
        r.unsubscribe()
        self.assertEqual(r.isSubscribed(), False)
        self.assertRaises(RuntimeError, r.unsubscribe)

    def testRegister(self):
        self.registrar.subscribe()
        self.assertEqual(self.hub.numRegistrations(), 0)
        content = zapi.traverse(self.rootFolder, "folder1/folder1_1")

        event = ObjectAddedEvent(content)
        self.events.publish(event)
        self.assertEqual(self.hub.numRegistrations(), 1)

    def testRegisterExisting(self):
        self.registrar.subscribe()
        self.registrar.registerExisting()
        # there are ten folders set up by PlacefulSetup that
        # should get registered
        self.assertEqual(self.hub.numRegistrations(), 10)

def test_suite():
    return makeSuite(TestRegistration)

if __name__=='__main__':
    main(defaultTest='test_suite')
