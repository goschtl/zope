from zope.testing import module
from zope.app.testing.functional import FunctionalTestSetup
from z3c.testsetup import register_all_tests
from megrok.login.tests import FunctionalLayer

def setUp(test):
    if test.filename.endswith('.txt'):
        module.setUp(test, '__main__')
    FunctionalTestSetup().setUp()
    
def tearDown(test):
    FunctionalTestSetup().tearDown()
    if test.filename.endswith('.txt'):
        module.tearDown(test)

test_suite = register_all_tests('megrok.login', layer=FunctionalLayer,
                                fextensions=['.txt', '.py'],
                                fsetup=setUp,
                                fteardown=tearDown
                                )
