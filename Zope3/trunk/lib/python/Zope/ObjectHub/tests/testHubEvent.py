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
$Id: testHubEvent.py,v 1.3 2002/10/21 06:14:48 poster Exp $
"""

import unittest, sys

from Zope.ObjectHub.HubEvent import ObjectRegisteredHubEvent
from Zope.ObjectHub.HubEvent import ObjectUnregisteredHubEvent
from Zope.ObjectHub.HubEvent import ObjectModifiedHubEvent
from Zope.ObjectHub.HubEvent import ObjectMovedHubEvent
from Zope.ObjectHub.HubEvent import ObjectRemovedHubEvent

from Zope.Exceptions import NotFoundError

class DummyObjectHub:

    def __init__(self, ruid, obj):
        self.ruid = ruid
        self.obj = obj
    
    
    def getObject(self, ruid):
        if ruid==self.ruid:
            return self.obj
            
        raise NotFoundError
        
class AbstractTestHubEvent(unittest.TestCase):
    
    location = '/some/location'
    hubid = 23
    obj = object()
    klass = None
    
    def setUp(self):
        objecthub = DummyObjectHub(self.hubid, self.obj)
        self.event = self.klass(objecthub, self.hubid, self.location)
        
    def testGetLocation(self):
        self.assertEqual(self.event.location, self.location)
        
    def testGetHubId(self):
        "Test hubid"
        self.assertEqual(self.event.hubid, self.hubid)
    
    def testGetObject(self):
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
