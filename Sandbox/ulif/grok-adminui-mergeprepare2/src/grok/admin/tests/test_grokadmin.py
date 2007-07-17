import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest, cleanup
import zope.component.eventtesting

def setUpZope(test):
    zope.component.eventtesting.setUp(test)

def cleanUpZope(test):
    cleanup.cleanUp()

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grok.admin.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUpZope,
                                    tearDown=cleanUpZope,
                                    optionflags=doctest.ELLIPSIS+
                                    doctest.NORMALIZE_WHITESPACE)

        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in []:
        suite.addTest(suiteFromPackage(name))
    for name in ['docgrok.txt']:
        suite.addTest(doctest.DocFileSuite(name,
                                           package='grok.admin',
                                           setUp=setUpZope,
                                           tearDown=cleanUpZope,
                                           optionflags=doctest.ELLIPSIS+
                                           doctest.NORMALIZE_WHITESPACE)
                      )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
