import grok
import unittest
import os.path

from martian.error import GrokImportError
from martian.directive import (MultipleTimesDirective, BaseTextDirective,
                               SingleValue, SingleTextDirective,
                               MultipleTextDirective,
                               MarkerDirective,
                               InterfaceDirective,
                               InterfaceOrClassDirective,
                               ModuleDirectiveContext,
                               ClassDirectiveContext,
                               ClassOrModuleDirectiveContext)
from martian import util
#from martian.scan import ModuleInfo

from pkg_resources import resource_listdir
from zope.testing import doctest
from zope.app.testing.functional import (HTTPCaller, getRootFolder,
                                         FunctionalTestSetup, sync, ZCMLLayer,
                                         FunctionalDocFileSuite)




class FunctionalDocTest(object):
    """A functional doc test, that will automatically executed.

    """

    ftesting_zcml = os.path.join(os.path.dirname(grok.__file__),
                                 'ftesting.zcml')
    FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                                'FunctionalLayer')
    
    def __init__(self):
        # print "FUNCDOCTEST CREATED: ", self
        pass
    
    def setUp(self, test):
        FunctionalTestSetup().setUp()

    def tearDown(self, test):
        return True
        FunctionalTestSetup().tearDown()

    def suiteFromFile(self, filepath):
        suite = unittest.TestSuite()
        # We must get the pkg of the target test...
        pkg = self.__module__.rsplit('.', 1)[0].replace('.', '/')
            
        test = FunctionalDocFileSuite(
            filepath, setUp=self.setUp, tearDown=self.tearDown,
            module_relative = True, package = pkg,
            globs = dict(http=HTTPCaller(),
                   getRootFolder=getRootFolder,
                   sync=sync
                   ),
            optionflags = (doctest.ELLIPSIS+
                           doctest.NORMALIZE_WHITESPACE+
                           doctest.REPORT_NDIFF)
            )
        test.layer = self.FunctionalLayer
        suite.addTest(test)
        return suite
        
    def test_suite(self):
        suite = unittest.TestSuite()
        for name in getattr(self, '__grok_testing_file__', []):
            suite.addTest(self.suiteFromFile(name))
        return suite
        

# Setup for the grok.testing.file directive...
all_func_doc_tests = []

def add_functional_doctest(doctest):
    all_func_doc_tests.append(doctest)

class TestingFileDirective(MultipleTextDirective):
    def check_arguments(self, filename = None):
        if filename is None or filename == '':
            raise GrokImportError("You must give a valid filename when using "
                                  "grok.testing.file() (invalid: %s)." % self.filename)

file = TestingFileDirective('grok.testing.file',
                            ClassOrModuleDirectiveContext())


def test_suite():

    suite = unittest.TestSuite()
    for klass in all_func_doc_tests:
        ftest = klass()
        suite.addTest(ftest.test_suite())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
