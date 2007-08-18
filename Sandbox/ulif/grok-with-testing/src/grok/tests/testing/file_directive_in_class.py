"""
Tests for the ``grok.testing.file`` directive in class context.

Declaring a not existent file makes Grok unhappy:

   >>> grok.grok(__name__)
   Traceback (most recent call last):
   ...
   GrokError: Doctest file ''Not existent file name'' declared in 'grok.tests.testing.file_directive_in_class' does not exist in '.../grok/tests/testing/'.

We don't *have* to use the ``grok.testing.file`` directive:

   >>> klass = DoctestWithoutFileDirective
   >>> hasattr(klass, '__grok_testing_file__')
   False

We can declare one or more doctest files per FunctionalDoctest. By
default doctestfiles are assumed to reside in the package of the
module in which the doctest was defined:

   >>> klass = DoctestInCurrentDir
   >>> hasattr(klass, '__grok_testing_file__')
   True

   >>> klassdoctests = getattr(klass, '__grok_testing_file__', [])
   >>> 'SampleDocTest.txt' in klassdoctests
   True

We can register doctests in subdirectories relative to the package of
the module, where the ``FunctionalDocTest`` was defined. To make use
of this feature, split path elements by the simple slash ('/').

The subdirectories do not have to be Python packages (although they
can), which is handy for functional tests, that should not be grokked
when running in non-testing mode:

   >>> klass = DoctestInSubDir
   >>> klassdoctests = getattr(klass, '__grok_testing_file__', [])
   >>> 'subdir/empty_doc_test.txt' in klassdoctests
   True

We can also register several docfiles per ``FunctionalDocTest``:

   >>> klass = DoctestWithSeveralTests
   >>> klassdoctests = getattr(klass, '__grok_testing_file__', [])
   >>> 'SampleDocTest.txt' in klassdoctests
   True

   >>> 'subdir/empty_doc_test.txt' in klassdoctests
   True

But if we try to register the same file several time, it will only be
registered once. To check this, we first 'delete' old doctests and
then grok this module:

   >>> len(grok.testing.all_doctest_infos)
   28

This is less than the amount of ``grok.testing.file`` directives seen
below.

Make sure, that doctest paths are looked up relative to the package,
where the declaring ``FunctionalDocTest`` was defined. To test this,
we grok the module in the subpackage and expect no ``GrokError`` to be
raised. This means, that the doctestfile was found, although it
resides in a different package and its path was declared relative to
the subpackage module.

   >>> dotted_subpkg_path = __name__.rsplit('.', 1)[0] + '.subpkg'
   >>> grok.grok(dotted_subpkg_path)

No output here is good. Just to make sure, the class was really
grokked:

   >>> from grok.tests.testing.subpkg.mod_declaring_a_doctest import DoctestDeclaredInSubpkg
   >>> klass = DoctestDeclaredInSubpkg
   >>> klassdoctests = getattr(klass, '__grok_testing_file__', [])
   >>> 'doctest_in_subpkg.txt' in klassdoctests
   True


"""

import grok

class DoctestWithoutFileDirective(grok.testing.FunctionalDocTest):
    pass

class NotExistentTestFile(grok.testing.FunctionalDocTest):
    grok.testing.file('Not existent file name')

class DoctestInCurrentDir(grok.testing.FunctionalDocTest):
    grok.testing.file('SampleDocTest.txt')

class DoctestInSubDir(grok.testing.FunctionalDocTest):
    grok.testing.file('subdir/empty_doc_test.txt')

class DoctestWithSeveralTests(grok.testing.FunctionalDocTest):
    grok.testing.file('SampleDocTest.txt')
    grok.testing.file('subdir/empty_doc_test.txt')

class DoctestWithOneTestSeveralTimes(grok.testing.FunctionalDocTest):
    grok.testing.file('SampleDocTest.txt')
    grok.testing.file('SampleDocTest.txt')
    grok.testing.file('SampleDocTest.txt')
    grok.testing.file('SampleDocTest.txt')

