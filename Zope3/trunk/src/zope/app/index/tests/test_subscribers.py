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
$Id: test_subscribers.py,v 1.2 2003/03/18 21:02:21 jim Exp $
"""

from unittest import makeSuite, main, TestCase

from zope.app.index.subscribers import Registration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse, locationAsTuple
from zope.app.event.objectevent import ObjectAddedEvent
from zope.component import getService
from zope.app.services.servicenames import EventPublication, HubIds

class TestRegistration(PlacefulSetup, TestCase):
    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.createStandardServices()
        r = Registration()
        default = traverse(self.rootFolder, '++etc++Services/default')
        default.setObject('registrar', r)
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
        content = object()
        name = 'blah'

        event = ObjectAddedEvent(content, locationAsTuple('/%s' %(name,)))
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
