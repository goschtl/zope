from zope.app.testing.functional import FunctionalDocFileSuite
from ticketcollector.testing import TicketCollectorLayer
import unittest

def test_suite():
    ticketcollector = FunctionalDocFileSuite("../README.txt")
    ticketcollector.layer = TicketCollectorLayer
    return unittest.TestSuite((
            ticketcollector,
            ))
