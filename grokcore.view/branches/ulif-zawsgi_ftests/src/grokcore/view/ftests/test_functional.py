import doctest
import re
import unittest
import os.path
import grokcore.view

from pkg_resources import resource_listdir
from zope.testing import doctest, renormalizing
#from zope.app.testing.functional import (HTTPCaller, getRootFolder,
#                                         FunctionalTestSetup, sync, ZCMLLayer)
from zope.app.wsgi.testlayer import BrowserLayer, http

ftesting_zcml = os.path.join(os.path.dirname(grokcore.view.__file__),
                             'ftesting.zcml')
#FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'FunctionalLayer',
#                            allow_teardown=True)
FunctionalLayer = BrowserLayer(grokcore.view, 'ftesting.zcml')
#FunctionalLayer = BrowserLayer(grokcore.view, ftesting_zcml)
#FunctionalLayer = BrowserLayer(grokcore.view)
#def setUp(test):
#    FunctionalTestSetup().setUp()

#def tearDown(test):
#    FunctionalTestSetup().tearDown()



checker = renormalizing.RENormalizing([
    # Accommodate to exception wrapping in newer versions of mechanize
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    getRootFolder = FunctionalLayer.getRootFolder
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grokcore.view.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname, #setUp=setUp, tearDown=tearDown,
            #checker=checker,
            extraglobs=dict(#http=HTTPCaller(),
                            http=http,
                            getRootFolder=getRootFolder,
                            #sync=sync),
                            ),
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF),
            )
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in ['view', 'staticdir', 'url', 'directoryresource']:
        suite.addTest(suiteFromPackage(name))
    return suite
