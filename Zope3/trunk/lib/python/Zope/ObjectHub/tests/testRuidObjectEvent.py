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
$Id: testRuidObjectEvent.py,v 1.2 2002/06/10 23:29:29 jim Exp $
"""

import unittest, sys

from Zope.ObjectHub.RuidObjectEvent import RuidObjectRegisteredEvent
from Zope.ObjectHub.RuidObjectEvent import RuidObjectUnregisteredEvent
from Zope.ObjectHub.RuidObjectEvent import RuidObjectAddedEvent
from Zope.ObjectHub.RuidObjectEvent import RuidObjectModifiedEvent
from Zope.ObjectHub.RuidObjectEvent import RuidObjectContextChangedEvent
from Zope.ObjectHub.RuidObjectEvent import RuidObjectRemovedEvent

from Zope.Exceptions import NotFoundError

class DummyObjectHub:

    def __init__(self, ruid, obj):
        self.ruid = ruid
        self.obj = obj
    
    
    def getObject(self, ruid):
        if ruid==self.ruid:
            return self.obj
            
        raise NotFoundError
        
class TestRuidObjectAddedEvent(unittest.TestCase):
    
    location = '/some/location'
    ruid = 23
    obj = object()
    klass = RuidObjectAddedEvent
    
    def setUp(self):
        objecthub = DummyObjectHub(self.ruid, self.obj)
        self.event = self.klass(objecthub, self.ruid, self.location)
        
    def testGetLocation(self):
        "Test getLocation method"
        self.assertEqual(self.event.getLocation(), self.location)
        
    def testGetRuid(self):
        "Test getRuid method"
        self.assertEqual(self.event.getRuid(), self.ruid)
    
    def testGetObject(self):
        "Test getObject method"
        self.assertEqual(self.event.getObject(), self.obj)
    
class TestRuidObjectRegisteredEvent(TestRuidObjectAddedEvent):

    klass = RuidObjectRegisteredEvent

class TestRuidObjectUnregisteredEvent(TestRuidObjectAddedEvent):

    klass = RuidObjectUnregisteredEvent

class TestRuidObjectModifiedEvent(TestRuidObjectAddedEvent):

    klass = RuidObjectModifiedEvent

class TestRuidObjectContextChangedEvent(TestRuidObjectAddedEvent):

    klass = RuidObjectContextChangedEvent

class TestRuidObjectRemovedEvent(TestRuidObjectAddedEvent):

    klass = RuidObjectRemovedEvent

    def setUp(self):
        self.event = self.klass(self.obj, self.ruid, self.location)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestRuidObjectAddedEvent),
        unittest.makeSuite(TestRuidObjectRegisteredEvent),
        unittest.makeSuite(TestRuidObjectUnregisteredEvent),
        unittest.makeSuite(TestRuidObjectModifiedEvent),
        unittest.makeSuite(TestRuidObjectContextChangedEvent),
        unittest.makeSuite(TestRuidObjectRemovedEvent),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
