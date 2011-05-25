import doctest
import megrok.login
import re
import unittest
from zope.testing import module, renormalizing
from zope.app.wsgi.testlayer import BrowserLayer

_layer = BrowserLayer(megrok.login, zcml_file='ftesting.zcml')

_checker = renormalizing.RENormalizing([
    # Relevant normalizers from zope.testing.testrunner.tests:
    (re.compile(r'\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
    # Our own one to work around
    # http://reinout.vanrees.org/weblog/2009/07/16/invisible-test-diff.html:
    (re.compile(r'.*1034h'), ''),
    (re.compile(r'httperror_seek_wrapper:'), 'HTTPError:' )
    ])

_option_flags = (
    doctest.ELLIPSIS +
    doctest.NORMALIZE_WHITESPACE +
    doctest.REPORT_NDIFF)

'''
def setUp(test):
    if test.filename.endswith('.txt'):
        module.setUp(test, '__main__')
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()
    if test.filename.endswith('.txt'):
        module.tearDown(test)
'''

def test_suite():
    suite = unittest.TestSuite()
    for name in [
        'megrok.login.tests.autoregister',
        'megrok.login.tests.customlogin',
        'megrok.login.tests.custompausetup',
        'megrok.login.tests.simple',
        'megrok.login.tests.strict',
        'megrok.login.tests.unset',
        ]:
        _globs = {'getRootFolder': _layer.getRootFolder}
        test = doctest.DocTestSuite(
            name,
            checker=_checker,
            globs=_globs,
            optionflags=_option_flags,
            )
        test.layer = _layer
        suite.addTest(test)
    return suite
