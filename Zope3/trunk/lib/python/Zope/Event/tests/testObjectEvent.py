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
$Id: testObjectEvent.py,v 1.3 2002/07/17 16:54:21 jeremy Exp $
"""

import unittest, sys

from Zope.Event.ObjectEvent import ObjectAddedEvent, ObjectModifiedEvent
from Zope.Event.ObjectEvent import ObjectRemovedEvent, ObjectMovedEvent

class TestObjectAddedEvent(unittest.TestCase):
    
    location = '/some/location'
    klass = ObjectAddedEvent
    
    def setUp(self):
        self.event = self.klass(self.location)
        
    def testGetLocation(self):
        "Test getLocation method"
        self.assertEqual(self.event.getLocation(),self.location)

class TestObjectModifiedEvent(TestObjectAddedEvent):

    klass = ObjectModifiedEvent

class TestObjectRemovedEvent(TestObjectAddedEvent):

    
    location = '/some/location'
    obj = object()
    
    def setUp(self):
        self.event = ObjectRemovedEvent(self.location, self.obj)
        
    def testGetLocation(self):
        "Test getLocation method"
        self.assertEqual(self.event.getLocation(),self.location)
        
    def testGetObject(self):
        "Test getObject method"
        self.assertEqual(self.event.getObject(), self.obj)



class TestObjectMovedEvent(TestObjectAddedEvent):

    from_location = '/some/other/location'
    
    def setUp(self):
        self.event = ObjectMovedEvent(self.from_location, self.location)

    def testFromLocation(self):
        "Test getFromLocation method"
        self.assertEqual(self.event.getFromLocation(),self.from_location)
        
def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestObjectAddedEvent),
                               unittest.makeSuite(TestObjectModifiedEvent),
                               unittest.makeSuite(TestObjectRemovedEvent),
                               unittest.makeSuite(TestObjectMovedEvent)))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
