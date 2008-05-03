from unittest import TestCase
from unittest import TestSuite
from unittest import makeSuite
from zope.interface.verify import verifyClass
from z3c.routes.route import Route
from z3c.routes.interfaces import IRoute

def DummyFactory(*args, **kwargs):
    return (args, kwargs)

class DummyRequest:
    def __init__(self, path=[]):
        self.path=path
        self.annotations={}

    def getTraversalStack(self):
        return self.path

    def setTraversalStack(self, path):
        self.path[:]=path



class ConstructorTests(TestCase):
    def testInterface(self):
        verifyClass(IRoute, Route)

    def testDottedFactory(self):
        route=Route("", "z3c.routes.tests.testRoute.test_suite")
        self.failUnless(route.factory is test_suite)

    def testFactoryMustBeCallable(self):
        self.assertRaises(TypeError, Route, None, ["not a factory"])

    def testCompileSimpleRoute(self):
        route=Route("/", DummyFactory)
        self.assertEqual(route._matcher.pattern, r"/\b")

    def testCompileRouteWithVariable(self):
        route=Route("/:model/view", DummyFactory)
        self.assertEqual(route._matcher.pattern, r"/(?P<model>[^/]+)/view\b")

    def testCompileRouteWithMultipleVariables(self):
        route=Route("/:model/view/:id", DummyFactory)
        self.assertEqual(route._matcher.pattern, r"/(?P<model>[^/]+)/view/(?P<id>[^/]+)\b")



class MatchTests(TestCase):
    def testSimpleString(self):
        route=Route("/view", DummyFactory)
        self.assertEqual(route.match("/view", DummyRequest()), True)
        self.assertEqual(route.match("/notview", DummyRequest()), False)

    def testPrefixElementDoesNotMatch(self):
        route=Route("/view", DummyFactory)
        self.assertEqual(route.match("/viewme", DummyRequest()), False)

    def testPrefixPathMatches(self):
        route=Route("/view", DummyFactory)
        self.assertEqual(route.match("/view/other", DummyRequest()), True)

    def testMatchPathStored(self):
        route=Route("/view", DummyFactory)
        request=DummyRequest()
        route.match("/view/other", request)
        self.assertEqual(request.annotations["z3c.routes.path"], "/view")

    def testVariablesExtracted(self):
        route=Route("/:model/view", DummyFactory)
        request=DummyRequest()
        route.match("/trains/view", request)
        request_variables=request.annotations["z3c.routes.variables"]
        self.assertEqual(request_variables.get("model", None), "trains")

    def testVariableExtractionDoesNotOverwriteDefaults(self):
        route=Route("/:model/view", DummyFactory, models="planes")
        route.match("/trains/view", DummyRequest())
        self.failUnless(route.variables.get("models", None), "planes")



class ExecuteTests(TestCase):
    def testVariablesPassedOn(self):
        route=Route("", DummyFactory, key="value")
        request=DummyRequest()
        request.annotations["z3c.routes.variables"]=dict(key="value")
        request.annotations["z3c.routes.path"]=""
        result=route.execute(request)
        self.assertEqual(result, ((), dict(key="value")))

    def testTraversalStackCleanSingleLevel(self):
        route=Route("", DummyFactory, key="value")
        request=DummyRequest(["branch", "leaf"])
        request.annotations["z3c.routes.variables"]=dict(key="value")
        request.annotations["z3c.routes.path"]="/toplevel"
        route.execute(request)
        self.assertEqual(request.path, ["branch", "leaf"])

    def testTraversalStackCleanedTwoLevels(self):
        route=Route("", DummyFactory, key="value")
        request=DummyRequest(["branch", "leaf"])
        request.annotations["z3c.routes.variables"]=dict(key="value")
        request.annotations["z3c.routes.path"]="/toplevel/branch"
        route.execute(request)
        self.assertEqual(request.path, ["leaf"])



def test_suite():
    suite=TestSuite()
    suite.addTest(makeSuite(ConstructorTests))
    suite.addTest(makeSuite(MatchTests))
    suite.addTest(makeSuite(ExecuteTests))
    return suite

