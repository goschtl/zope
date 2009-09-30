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

- ``include``: list of packages to include (whitespace-separated)
  (default: empty)
- ``exclude``: packages matching any regex in this list will be excluded
  (default: empty)
- ``script``: the name of the runner script (defaults to the part name)

>>> cd(sample_buildout)
>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... """)

>>> 'Installing compattest' in system(buildout)
True

Details
=======

The recipe generates a test runner for each package, as well as a global runner
script (called `test-compat` by default) that will run all of them:

>>> ls('bin')
- buildout
- compattest
- compattest-z3c.recipe.compattest

>>> cat('bin', 'compattest')
#!...python...
...main(...compattest-z3c.recipe.compattest...

We take care about installing the test dependencies for the packages
(from their ``extras_require['test']``). Do demonstrate this, we
declared a (superfluous) test dependency on ``zope.dottedname``, which is
picked up:

>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!...python...
...zope.dottedname...


Passing options to the test runners
===================================

If you want to use custom options in the generated test runners, you can specify
them in the part options, prefixed by ``runner-``. That is, if you want to pass
the ``--foo`` option by default to all generated test runners, you can set
``runner-defaults = ['--foo']`` in your part:

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest
...
... [compattest]
... recipe = z3c.recipe.compattest
... include = z3c.recipe.compattest
... runner-defaults = ['-c', '-v', '-v']
... """)
>>> ignore = system(buildout)
>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!...python...
...run(...['-c', '-v', '-v']...

Every options prefixed by ``runner-`` will be automatically passed to the
generated test runners.
