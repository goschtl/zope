import unittest
from zope.app.testing import functional
from ZODB.interfaces import IDatabase
from zope import component
import ZODB.tests.util
functional.defineLayer('TestLayer', 'ftesting.zcml')

def setUp(test):
    databases = test.globs['getRootFolder']()._p_jar.db().databases
    db2 = ZODB.tests.util.DB(databases=databases, database_name='2')

    for name, db in databases.items():
        component.provideUtility(db, IDatabase, name=name)


def test_suite():
    suite = unittest.TestSuite()
    suites = (
        functional.FunctionalDocFileSuite('browser/README.txt', setUp=setUp),
        )
    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
