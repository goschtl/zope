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

from pkg_resources import resource_listdir
from zope.testing import doctest
from zope.app.testing.functional import (HTTPCaller, getRootFolder,
                                         FunctionalTestSetup, sync, ZCMLLayer,
                                         FunctionalDocFileSuite)

class FunctionalDocTest(object):
    """A functional doc test, that will be automatically executed.
    """

    ftesting_zcml = os.path.join(os.path.dirname(grok.__file__),
                                 'ftesting.zcml')
    FunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                                'FunctionalLayer')

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
        
    def __grok_test_suite__(self):
        suite = unittest.TestSuite()
        for name in getattr(self, '__grok_testing_file__', []):
            suite.addTest(self.suiteFromFile(name))
        return suite
        

class FunctionalDocTestForModule(FunctionalDocTest):
    """A doctest with a given pkg and docfile path.
    """
    pkg = None
    filepath = None
    
    def __init__(self, pkg, filepath):
        self.pkg = pkg
        self.filepath = filepath

    def __grok_test_suite__(self):
        suite = unittest.TestSuite()
        for path in self.filepath:
            test = FunctionalDocFileSuite(
                path, setUp=self.setUp, tearDown=self.tearDown,
                module_relative = True, package = self.pkg,
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


# Setup for the grok.testing.file directive.
#
# This is a list of FunctionalDocTest classes and tuples containing a
# dotted pkg name and a filepath. The first is injected by the testing
# class grokker, while the latter is injected by module wide
# directives.
all_func_doc_tests = set()
all_func_doc_test_locations = []

def add_functional_doctest(doctest):
    # TODO: a set does not check hard enough for existing tests.
    all_func_doc_tests.add(doctest)

def add_functional_doctest_location(pkg, subpath):
    # TODO: check harder for existing tests.
    if subpath == []:
        return
    if (pkg, subpath) in all_func_doc_test_locations:
        return
    all_func_doc_test_locations.append((pkg, subpath))


class TestingFileDirective(MultipleTextDirective):
    def check_arguments(self, filename = None):
        if filename is None or filename == '':
            raise GrokImportError("You must give a valid filename when using "
                                  "grok.testing.file() (invalid: '%s')." % (
                filename,))

file = TestingFileDirective('grok.testing.file',
                            ClassOrModuleDirectiveContext())


def test_suite():
    suite = unittest.TestSuite()
    # First handle doctests registered on module level...
    for elem in all_func_doc_test_locations:
        pkg, path = elem
        ftest = FunctionalDocTestForModule(pkg, path)
    # Then handle doctests registered on class level...
    for klass in all_func_doc_tests:
        # This klass describes a class, which is derived from
        # ``FunctionalDocTest`` and brings all neccessary methods
        # to extract tests with it.
        ftest = klass()
        suite.addTest(ftest.__grok_test_suite__())
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
