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
"""Test suite for Zope.Event.Logger.

$Id: testLogger.py,v 1.9 2002/12/20 15:58:21 gvanrossum Exp $
"""

import unittest
import logging

from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getServiceManager, getService

from Zope.Event import globalSubscribe, unsubscribe, publish
from Zope.Event.ObjectEvent import ObjectAddedEvent
from Zope.Event.Logger import Logger

from Zope.Event.GlobalEventService import GlobalEventService

class DopeyHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self.results = []

    def emit(self, record):
        self.results.append(record)

class TestLogger1(PlacelessSetup,unittest.TestCase):

    eventlogger = Logger()

    def setUp(self):
        PlacelessSetup.setUp(self)
        from Zope.Event.IEventService import IEventService
        getServiceManager(None).defineService("Events", IEventService)
        from Zope.Event.GlobalEventService import eventService
        getServiceManager(None).provideService("Events", eventService)
        # futz a handler in for testing
        self.logger = logging.getLogger("Event.Logger")
        self.oldlevel = self.logger.level
        self.oldprop = self.logger.propagate
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)
        self.handler = DopeyHandler()
        self.logger.addHandler(self.handler)
        # register a logger
        globalSubscribe(self.eventlogger)
        # send an event
        publish(None, ObjectAddedEvent(None, 'foo'))

    def tearDown(self):
        unsubscribe(self.eventlogger)
        self.logger.removeHandler(self.handler)
        self.logger.setLevel(self.oldlevel)
        self.logger.propagate = self.oldprop
        PlacelessSetup.tearDown(self)

    def testLogger(self):
        # Test the logger logs appropriately
        results = self.handler.results
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.name, "Event.Logger")
        self.assertEqual(result.levelno, logging.INFO)
        self.assertEqual(result.getMessage(),
                         "Zope.Event.ObjectEvent.ObjectAddedEvent: "
                         "XXX detail temporarily disabled\n")
        self.assertEqual(result.exc_info, None)

class TestLogger2(TestLogger1):

    eventlogger = Logger(logging.CRITICAL)

    def testLogger(self):
        # Test the logger logs appropriately
        results = self.handler.results
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.name, "Event.Logger")
        self.assertEqual(result.levelno, logging.CRITICAL)
        self.assertEqual(result.getMessage(),
                         "Zope.Event.ObjectEvent.ObjectAddedEvent: "
                         "XXX detail temporarily disabled\n")
        self.assertEqual(result.exc_info, None)

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestLogger1),
        unittest.makeSuite(TestLogger2),
        ])

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
