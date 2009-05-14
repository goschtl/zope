##########################################################################
# zopyx.smartprintng.core 
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################


"""
Tests, tests, tests.........
"""

import os
import unittest

from zope.component import adapter
from zope.interface import implements, Interface, implementer
from zope.app.testing import ztapi

from zopyx.smartprintng.core.aggregation import aggregateHTML
from zopyx.smartprintng.core.interfaces import IHTMLExtractor

class IDummyInterface(Interface):
    pass

class DummyContent(object):
    implements(IDummyInterface)

class DummyContent2(object):
    pass

class DummyAdapter(object):

    implements(IHTMLExtractor)

    def __init__(self, context):
        self.context = context

    def getHTML(self):
        return '<h1>hello world</h1>'


class AggregationTests(unittest.TestCase):

    def testAggregationWithRegisteredAdapter(self):
        ztapi.provideAdapter(IDummyInterface, IHTMLExtractor, DummyAdapter)
        obj = DummyContent()
        self.assertEqual(IDummyInterface.implementedBy(DummyContent), True)
        html = aggregateHTML(obj)
        self.assertEqual(html, '<h1>hello world</h1>')

    def testAggregationWithoutRegisteredAdapter(self):

        obj = DummyContent2()
        html = aggregateHTML(obj)
        self.assertEqual(html, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AggregationTests))
    return suite

