from unittest import TestCase
from unittest import TestSuite
from unittest import makeSuite
from zope.component import provideAdapter
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.testing.cleanup import CleanUp
from zope.interface.verify import verifyClass
from zope.publisher.interfaces import IPublishTraverse
from z3c.routes.traverser import RouteTraverser
from z3c.routes.interfaces import IRoutingRoot
from zope.publisher.interfaces import NotFound

class DummyRequest:
    def getTraversalStack(self):
        return []

class NothingRouter(object):
    implements(IRoutingRoot)
    adapts(Interface)

    def __init__(self, context):
        pass
    def routes(self):
        return []


class TraversalTests(TestCase, CleanUp):
    def testInterface(self):
        verifyClass(IPublishTraverse, RouteTraverser)

    def testNotFoundRaisedIfNothingMatches(self):
        provideAdapter(NothingRouter)
        traverser=RouteTraverser(None, None)
        self.assertRaises(NotFound,
                          traverser.publishTraverse, DummyRequest(), "nothere")


def test_suite():
    suite=TestSuite()
    suite.addTest(makeSuite(TraversalTests))
    return suite
