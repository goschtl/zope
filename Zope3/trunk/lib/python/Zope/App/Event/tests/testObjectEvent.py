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
$Id: testObjectEvent.py,v 1.1 2002/12/21 15:32:45 poster Exp $
"""

import unittest, sys

from Zope.App.Event.ObjectEvent import ObjectAddedEvent
from Zope.App.Event.ObjectEvent import ObjectModifiedEvent
from Zope.App.Event.ObjectEvent import ObjectRemovedEvent
from Zope.App.Event.ObjectEvent import ObjectMovedEvent
from Zope.App.Event.ObjectEvent import ObjectAnnotationsModifiedEvent
from Zope.App.Event.ObjectEvent import ObjectContentModifiedEvent

class TestObjectAddedEvent(unittest.TestCase):
    
    location = '/some/location'
    object = object()
    klass = ObjectAddedEvent
    
    def setUp(self):
        self.event = self.klass(self.object, self.location)
        
    def testGetLocation(self):
        self.assertEqual(self.event.location, self.location)
        
    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)

class TestObjectModifiedEvent(TestObjectAddedEvent):

    klass = ObjectModifiedEvent

class TestObjectAnnotationsModifiedEvent(TestObjectAddedEvent):
    klass = ObjectAnnotationsModifiedEvent

class TestObjectContentModifiedEvent(TestObjectAddedEvent):
    klass = ObjectContentModifiedEvent


class TestObjectRemovedEvent(TestObjectAddedEvent):

    
    location = '/some/location'
    
    def setUp(self):
        self.event = ObjectRemovedEvent(self.object, self.location)
        
    def testGetLocation(self):
        self.assertEqual(self.event.location, self.location)
        
    def testGetObject(self):
        self.assertEqual(self.event.object, self.object)



class TestObjectMovedEvent(TestObjectAddedEvent):

    from_location = '/some/other/location'
    
    def setUp(self):
        self.event = ObjectMovedEvent(self.object,
                                      self.from_location, self.location)

    def testFromLocation(self):
        self.assertEqual(self.event.fromLocation, self.from_location)
        
def test_suite():
    return unittest.TestSuite((unittest.makeSuite(TestObjectAddedEvent),
                               unittest.makeSuite(TestObjectModifiedEvent),
                               unittest.makeSuite(TestObjectAnnotationsModifiedEvent),
                               unittest.makeSuite(TestObjectContentModifiedEvent),
                               unittest.makeSuite(TestObjectRemovedEvent),
                               unittest.makeSuite(TestObjectMovedEvent)))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
