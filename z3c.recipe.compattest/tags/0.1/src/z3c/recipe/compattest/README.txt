=====================
z3c.recipe.compattest
=====================

This buildout recipe generates a list of packages to test and a test runner
that runs each package's tests (isolated from any other tests).
This is useful to check that the changes made while developing a package
do not break any packages that are using this package.

Usage
=====

Add a part to your buildout.cfg that uses this recipe.
No further configuration is required, but you can set the following options:

- ``svn_url``: SVN repository to search for packages,
- ``include``: only packages matching this regex will be included
  (default:``^zope\..*``, ``^grokcore\..*``),
- ``exclude``: packages matching this regex will be excluded, even if
  they match ``include`` (default: a list of deprectated/obsolete
  ``zope.*`` packages, see ``z3c.recipe.compattest.recipe`` for
  details),
- ``script``: the name of the runner script (default: test-compat).

>>> cd(sample_buildout)
>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... """)

For this test, we only include a single package. With the default
include/exclude values, about 150 packages will be included, so be aware
that running the buildout will take some time.

>>> system(buildout).find('Installing compattest') != -1
True

Details
=======

The recipe generates a test runner for each package, as well as a global runner
script (called `test-compat` by default) that will run all of them:

>>> ls('bin')
- buildout
- compattest-z3c.recipe.compattest
- test-compat
>>> cat('bin', 'test-compat')
#!/...python...
...main(...compattest-z3c.recipe.compattest...

We take care about installing the test dependencies for the packages
(from their ``extras_require['test']``). Do demonstrate this, we
declared a (superfluous) test dependency on ``zope.dottedname``, which is
picked up:

>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!/...python...
...zope.dottedname...
