"""
Tests for the ``grok.testing.file`` directive in module context.


   >>> import grok
   >>> grok.grok(__name__)

We can declare one or more doctest files per module. By default
doctestfiles are assumed to reside in the package of the module in
which the doctest was declared:

   >>> 'SampleDocTest.txt' in __grok_testing_file__
   True

   >>> 'AnotherSampleTest.txt' in  __grok_testing_file__
   True

The registered tests are stored in
``grok.testing.all_func_doc_test_locations``. This is where we can
look for what really got registered.

   >>> pathlist = [x.docfile_path for x in grok.testing.all_doctest_infos]
   >>> 'AnotherSampleTest.txt' in pathlist
   True


We can register doctests in subdirectories relative to the package of
the module, where the file was declared. To make use
of this feature, split path elements by the simple slash ('/').

   >>> 'subpkg/doctest_in_subpkg.txt' in pathlist
   True

The subdirectories do not have to be Python packages (although they
can), which is handy for functional tests, that should not be grokked
when running in non-testing mode:

   >>> 'subdir/empty_doc_test.txt' in pathlist
   True

We can also register several docfiles per module. But if we try to
register the same file several time, it will only be registered
once. We declared ``SampleDocTest.txt`` several times below, but:

   >>> len([x for x in pathlist if x == 'SampleDocTest.txt'])
   2


"""

import grok

grok.testing.file('SampleDocTest.txt')
grok.testing.file('SampleDocTest.txt')
grok.testing.file('AnotherSampleTest.txt')
grok.testing.file('subdir/empty_doc_test.txt')
grok.testing.file('subpkg/doctest_in_subpkg.txt')


