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
$Id: testHubEvent.py,v 1.2 2002/10/03 20:53:23 jim Exp $
"""

import unittest, sys

from Zope.ObjectHub.HubEvent import ObjectRegisteredHubEvent
from Zope.ObjectHub.HubEvent import ObjectUnregisteredHubEvent
from Zope.ObjectHub.HubEvent import ObjectAddedHubEvent
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
        
class TestObjectAddedHubEvent(unittest.TestCase):
    
    location = '/some/location'
    ruid = 23
    obj = object()
    klass = ObjectAddedHubEvent
    
    def setUp(self):
        objecthub = DummyObjectHub(self.ruid, self.obj)
        self.event = self.klass(objecthub, self.ruid, self.location)
        
    def testGetLocation(self):
        self.assertEqual(self.event.location, self.location)
        
    def testGetRuid(self):
        self.assertEqual(self.event.hid, self.ruid)
    
    def testGetObject(self):
        self.assertEqual(self.event.object, self.obj)
    
class TestObjectRegisteredHubEvent(TestObjectAddedHubEvent):

    klass = ObjectRegisteredHubEvent

class TestObjectUnregisteredHubEvent(TestObjectAddedHubEvent):

    klass = ObjectUnregisteredHubEvent

class TestObjectModifiedHubEvent(TestObjectAddedHubEvent):

    klass = ObjectModifiedHubEvent

class TestObjectMovedHubEvent(TestObjectAddedHubEvent):

    klass = ObjectMovedHubEvent

class TestObjectRemovedHubEvent(TestObjectAddedHubEvent):

    klass = ObjectRemovedHubEvent

    def setUp(self):
        self.event = self.klass(self.obj, self.ruid, self.location)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestObjectAddedHubEvent),
        unittest.makeSuite(TestObjectRegisteredHubEvent),
        unittest.makeSuite(TestObjectUnregisteredHubEvent),
        unittest.makeSuite(TestObjectModifiedHubEvent),
        unittest.makeSuite(TestObjectMovedHubEvent),
        unittest.makeSuite(TestObjectRemovedHubEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
