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

$Id: test_logger.py,v 1.2 2002/12/25 14:12:51 jim Exp $
"""

import unittest
import logging

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getServiceManager, getService

from zope.app.event import globalSubscribe
from zope.event import unsubscribe, publish
from zope.app.event.objectevent import ObjectAddedEvent
from zope.app.event.logger import Logger

from zope.app.event.globaleventservice import GlobalEventService

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
        from zope.interfaces.event import IEventService
        getServiceManager(None).defineService("Events", IEventService)
        from zope.app.event.globaleventservice import eventService
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
                         "zope.app.event.objectevent.ObjectAddedEvent: "
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
                         "zope.app.event.objectevent.ObjectAddedEvent: "
                         "XXX detail temporarily disabled\n")
        self.assertEqual(result.exc_info, None)

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestLogger1),
        unittest.makeSuite(TestLogger2),
        ])

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
