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
$Id: test_logger.py,v 1.10 2003/06/30 20:48:39 jeremy Exp $
"""

import unittest
import logging

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component import getServiceManager
from zope.app.services.servicenames import EventPublication

from zope.app.event import globalSubscribe, globalUnsubscribe, publish
from zope.app.event.objectevent import ObjectAddedEvent
from zope.app.event.globalservice import Logger

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
        from zope.app.interfaces.event import IPublisher
        getServiceManager(None).defineService(EventPublication, IPublisher)
        from zope.app.event.globalservice import eventPublisher
        getServiceManager(None).provideService(EventPublication, eventPublisher)
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
        globalUnsubscribe(self.eventlogger)
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
                         "[('_ObjectEvent__location', 'foo'), "
                         "('object', None)]\n")
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
                         "[('_ObjectEvent__location', 'foo'), "
                         "('object', None)]\n")
        self.assertEqual(result.exc_info, None)

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestLogger1),
        unittest.makeSuite(TestLogger2),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
