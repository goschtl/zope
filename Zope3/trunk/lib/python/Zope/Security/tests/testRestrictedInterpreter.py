import unittest

from Zope.Security.RestrictedInterpreter import RestrictedInterpreter
from Zope.Security.Proxy import ProxyFactory
from Zope.Security.Checker import defineChecker

from Zope.Testing.CleanUp import cleanUp

class RITests(unittest.TestCase):

    def setUp(self):
        self.rinterp = RestrictedInterpreter()

    def tearDown(self):
        cleanUp()

    def testExec(self):
        self.rinterp.ri_exec("str(type(1))\n")

    def testImport(self):
        self.rinterp.ri_exec("import Zope.Security.Proxy")

    def testWrapping(self):
        # make sure we've really got proxies
        import types
        from Zope.Security.Checker import NamesChecker

        checker = NamesChecker(['Proxy'])

        import Zope.Security.Proxy
        defineChecker(Zope.Security.Proxy, checker)

        checker = NamesChecker(['BuiltinFunctionType'])
        defineChecker(types, checker)

        code = ("from Zope.Security.Proxy import Proxy\n"
                "import types\n"
                "assert type(id) is not types.BuiltinFunctionType\n"
                )
        self.rinterp.ri_exec(code)

def test_suite():
    return unittest.makeSuite(RITests)


if __name__=='__main__':
    from unittest import main
    main(defaultTest='test_suite')
