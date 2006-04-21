import unittest
from cStringIO import StringIO

from zope import component

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.testing.doctestunit import DocTestSuite
from zope.app.testing.placelesssetup import PlacelessSetup

import zalchemy
from zalchemy.interfaces import IAlchemyEngineUtility

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:test='http://www.zope.org/NS/Zope3/test'
   xmlns:alchemy='http://namespaces.zalchemy.org/alchemy'
   i18n_domain='zope'>
   %s
   </configure>"""

class TestDirectives(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestDirectives, self).setUp()
        XMLConfig('meta.zcml', zalchemy)()

    def testEngineDirective(self):
        xmlconfig(StringIO(template % (
            '''
            <alchemy:engine
                name="sqlite"
                dns="sqlite"
                echo="True"
                filename="testdatabase.db"
                />
            '''
            )))
        util = component.getUtility(IAlchemyEngineUtility,'sqlite')
        self.assertNotEqual(util, None)
        self.assertEqual(util.dns, 'sqlite')
        self.assertEqual(util.echo, True)
        self.assertEqual(util.kw['filename'], 'testdatabase.db')

    def testConnectDirective(self):
        from environ import testTable
        self.assertRaises(AttributeError,
                lambda : testTable.engine.engine)
        xmlconfig(StringIO(template % (
            '''
            <alchemy:engine
                name="sqlite-in-memory"
                dns="sqlite://:memory:"
                />
            <alchemy:connect
                engine="sqlite-in-memory"
                table="zalchemy.tests.environ.testTable"
                />
            '''
            )))
        util = component.getUtility(IAlchemyEngineUtility,'sqlite-in-memory')
        self.assert_(len(util.tables)==1)
        self.assertEqual(util.tables[0],
                         zalchemy.tests.environ.testTable)

    def tearDown(self):
        PlacelessSetup.tearDown(self)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestDirectives),
        #DocTestSuite(),
        ))

if __name__ == "__main__":
    unittest.TextTestRunner().run(test_suite())

