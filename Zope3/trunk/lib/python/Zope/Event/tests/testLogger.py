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
$Id: testLogger.py,v 1.2 2002/06/10 23:29:26 jim Exp $
"""

import unittest, sys
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getServiceManager, getService

from Zope.Event import subscribe, unsubscribe, publishEvent
from Zope.Event.ObjectEvent import ObjectAddedEvent
from Zope.Event.Logger import Logger

import zLOG
from zLOG import BLATHER, PANIC

from Zope.Event.GlobalEventService import GlobalEventService

class DopeyLogger:

    def __init__(self):
        self.result=[]
        
    def log_write(self, subsystem, severity, summary, detail, error):
        self.result.append((subsystem,severity,summary,detail,error))
        
class TestLogger1(PlacelessSetup,unittest.TestCase):

    eventlogger = Logger()
    
    def setUp(self):
        PlacelessSetup.setUp(self)
        from Zope.Event.IEventService import IEventService
        getServiceManager(None).defineService("Events", IEventService)
        from Zope.Event.GlobalEventService import eventService
        getServiceManager(None).provideService("Events", eventService)
        # futz a logger in for testing
        self.__old_log_write = zLOG.log_write
        self.logger = DopeyLogger()
        zLOG.log_write = self.logger.log_write
        # register a logger
        subscribe(self.eventlogger)
        # send an event
        publishEvent(None, ObjectAddedEvent('foo'))

    def tearDown(self):
        unsubscribe(self.eventlogger)
        zLOG.log_write = self.__old_log_write
        PlacelessSetup.tearDown(self)
        
    def testLogger(self):
        "Test the logger logs appropriately"
        # check the dopey logger
        self.assertEqual(self.logger.result,
                         [
            (
            'Event.Logger',
            BLATHER,
            'Zope.Event.ObjectEvent.ObjectAddedEvent',
            "{'_ObjectAddedEvent__location': 'foo'}\n",
            None,
            )
            ])

class TestLogger2(TestLogger1):

    eventlogger = Logger(PANIC)

    def testLogger(self):
        "Test the logger logs appropriately"
        # check the dopey logger
        self.assertEqual(self.logger.result,
                         [
            (
            'Event.Logger',
            PANIC,
            'Zope.Event.ObjectEvent.ObjectAddedEvent',
            "{'_ObjectAddedEvent__location': 'foo'}\n",
            None,
            )
            ])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestLogger1),
        unittest.makeSuite(TestLogger2),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
