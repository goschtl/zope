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
from martian import util, scan

from pkg_resources import resource_listdir
import zope.component.eventtesting
from zope.testing import doctest, cleanup
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
        FunctionalTestSetup().tearDown()

    def suiteFromFile(self, module_info, filepath):
        suite = unittest.TestSuite()
        test = FunctionalDocFileSuite(
            filepath, setUp=self.setUp, tearDown=self.tearDown,
            module_relative = True,
            package = module_info.package_dotted_name,
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
        
    def grok_test_suite(self, fdoctest_info):
        suite = unittest.TestSuite()
        suite.addTest(self.suiteFromFile(
            fdoctest_info.module_info,
            fdoctest_info.docfile_path))
        return suite


class UnitDocTest(object):
    """A unit doc test, that will be automatically executed.
    """


    optionflags = (doctest.ELLIPSIS+
                   doctest.NORMALIZE_WHITESPACE)

    def setUp(self, test):
        zope.component.eventtesting.setUp(test)

    def tearDown(self, test):
        cleanup.cleanUp()

    def suiteFromFile(self, module_info, filepath):
        suite = unittest.TestSuite()
        test = doctest.DocFileSuite(
            filepath,
            package=module_info.package_dotted_name,
            setUp=self.setUp,
            tearDown=self.tearDown,
            optionflags = self.optionflags
            )
        suite.addTest(test)
        return suite
        
    def grok_test_suite(self, unitdoctest_info):
        suite = unittest.TestSuite()
        suite.addTest(
            self.suiteFromFile(unitdoctest_info.module_info,
                               unitdoctest_info.docfile_path)
            )
        return suite


class DocTestInfo(object):
    """Base for information about doctests of some kind.

    DocTestInfos store some more information about doctests, than only
    the doctest filepath. The ``klass`` is one of the more specialized
    DocTest classes implemented above. It is responsible for setup of
    tests for a certain test. The module_info is of use for computing
    package paths and similar.
    """
    module_info = None
    klass = None
    docfile_path = None

    doctest_class = None

    def __init__(self, module_info, docfile_path, klass):
        if not isinstance(klass, self.doctest_class):
            klass = self.doctest_class
        self.module_info = module_info
        self.klass = klass
        self.docfile_path = docfile_path

    def absoluteDocFilePath(self):
        return self.module_info.getResourcePath(self.docfile_path)


class UnitDocTestInfo(DocTestInfo):
    """Information about a unit doctest.

    If klass is not a UnitDocTest (or derived), it will be replaced by
    a UnitDocTest. We need this when ``ModuleGrokkers`` provide their
    factory as klass, which means: a module.
    """
    doctest_class = UnitDocTest


class FunctionalDocTestInfo(DocTestInfo):
    """Information about a functional doctest.

    If klass is not a FunctionalDocTest (or derived), it will be
    replaced by a FunctionalDocTest. We need this when
    ``ModuleGrokkers`` provide their factory as klass, which means: a
    module.
    """
    doctest_class=FunctionalDocTest


# Setup for the grok.testing.file directive.
#
# This is a list of DocTestInfo objects. We read it in our global
# ``test_suite()`` function, when the testrunner asks for it. The
# objects are injected by appropriate grokkers in meta.py.
all_doctest_infos = []


# This is the recommended way to add objects to the above list. Thus,
# we can incorporate local checks (for duplicates or whatever) here,
# without hassle elsewhere.
#
# A duplicate checker is easy to do, but intentionally left out: if a
# developer wants to run a test twice, s/he will have reasons for it.
# We will not try to be smarter.
def add_doctest_info(doctest_info):
    all_doctest_infos.append(doctest_info)


class TestingFileDirective(MultipleTextDirective):
    def check_arguments(self, filename = None):
        if filename is None or filename == '':
            raise GrokImportError("You must give a valid filename when using "
                                  "grok.testing.file() (invalid: '%s')." % (
                filename,))

file = TestingFileDirective('grok.testing.file',
                            ClassOrModuleDirectiveContext())


def test_suite():
    """Our hook into the testrunner.
    """
    suite = unittest.TestSuite()

    for info in all_doctest_infos:
        doctest = info.klass()
        suite.addTest(doctest.grok_test_suite(info))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
