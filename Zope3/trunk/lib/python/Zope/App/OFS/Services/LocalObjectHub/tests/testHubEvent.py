##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: testHubEvent.py,v 1.1 2002/10/21 06:14:47 poster Exp $
"""

# in the local version of these tests, we are no longer using a fake
# ObjectHub, which makes these tests less pure...but still useful
# as a test for both the events and the object hub now.

import unittest, sys
from ObjectHubSetup import ObjectHubSetup
from Zope.App.OFS.Services.LocalObjectHub.LocalHubEvent import \
     ObjectRegisteredHubEvent, ObjectUnregisteredHubEvent, \
     ObjectModifiedHubEvent, ObjectMovedHubEvent, \
     ObjectRemovedHubEvent
from Zope.App.Traversing import getPhysicalPathString

from Zope.Exceptions import NotFoundError
from Zope.ComponentArchitecture import getService
        
class AbstractTestHubEvent(ObjectHubSetup, unittest.TestCase):
    
    klass = None
    
    def setUp(self):
        ObjectHubSetup.setUp(self)
        self.object_hub = getService(self.rootFolder, "ObjectHub")
        self.obj = self.folder1_2_1
        self.hubid = self.object_hub.register(self.obj)
        self.location = getPhysicalPathString(self.obj)
        self.event = self.klass(self.object_hub, self.hubid, self.location)
        
    def testGetLocation(self):
        "Test getLocation method"
        self.assertEqual(self.event.location, self.location)
        
    def testGetHubId(self):
        "Test getHubId method"
        self.assertEqual(self.event.hubid, self.hubid)
    
    def testGetObject(self):
        "Test getObject method"
        self.assertEqual(self.event.object, self.obj)
    
class TestObjectRegisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectRegisteredHubEvent

class TestObjectUnregisteredHubEvent(AbstractTestHubEvent):

    klass = ObjectUnregisteredHubEvent

class TestObjectModifiedHubEvent(AbstractTestHubEvent):

    klass = ObjectModifiedHubEvent

class TestObjectMovedHubEvent(AbstractTestHubEvent):

    klass = ObjectMovedHubEvent

class TestObjectRemovedHubEvent(AbstractTestHubEvent):

    klass = ObjectRemovedHubEvent

    def setUp(self):
        AbstractTestHubEvent.setUp(self)
        self.event = self.klass(self.obj, self.hubid, self.location)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectRegisteredHubEvent),
        unittest.makeSuite(TestObjectUnregisteredHubEvent),
        unittest.makeSuite(TestObjectModifiedHubEvent),
        unittest.makeSuite(TestObjectMovedHubEvent),
        unittest.makeSuite(TestObjectRemovedHubEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
