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
- ``include``: only packages matching a regex in this list (one regex per line)
  will be included (default:``^zope\..*``, ``^grokcore\..*``),
- ``exclude``: packages matching any regex in this list will be excluded, even if
  they match ``include`` (default: a list of deprectated/obsolete
  ``zope.*`` packages, see ``z3c.recipe.compattest.recipe`` for
  details),
- ``script``: the name of the runner script (default: test-compat).

- ``use_svn``: use SVN checkouts instead of releases (see below)
- ``svn_directory``: directory to place checkouts in (default: parts/<partname>)

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

>>> print system(buildout)
Couldn't...Installing compattest...

Details
=======

The recipe generates a test runner for each package, as well as a global runner
script (called `test-compat` by default) that will run all of them:

>>> ls('bin')
- buildout
- compattest-z3c.recipe.compattest
- test-compattest
>>> cat('bin', 'test-compattest')
#!/...python...
...main(...compattest-z3c.recipe.compattest...

We take care about installing the test dependencies for the packages
(from their ``extras_require['test']``). Do demonstrate this, we
declared a (superfluous) test dependency on ``zope.dottedname``, which is
picked up:

>>> cat('bin', 'compattest-z3c.recipe.compattest')
#!/...python...
...zope.dottedname...

Using SVN checkouts
===================

When you set ``use_svn`` to true, the test runners will not refer to released
eggs, but rather use development-egg links to SVN checkouts of the trunks of
each package (the checkouts are placed in ``svn_directory``).

Note: Even though the generated testrunners will use development-egg links, this
does not change the develop-eggs for your buildout itself. We check that before
the installation of the recipe, there's just the single develop-egg link of the
package we're working on:

>>> ls('develop-eggs')
- z3c.recipe.compattest.egg-link

>>> write('buildout.cfg', """
... [buildout]
... parts = compattest-trunk
...
... [compattest-trunk]
... recipe = z3c.recipe.compattest
... include = zope.dottedname
...           z3c.recipe.compattest
... use_svn = true
... """)
>>> ignore = system(buildout)

The checkouts are placed in the ``parts/`` folder by default, but you can
override this by setting ``svn_directory`` -- so you can share checkouts
between several buildouts, for example.

Note that for packages that already exist as develop eggs (in our example,
z3c.recipe.compattest), no checkout is performed.

>>> ls('parts/compattest-trunk')
d zope.dottedname

The testrunner uses the checked out version of zope.dottedname:

>>> cat('bin', 'compattest-trunk-zope.dottedname')
#!/...python...
...parts/compattest-trunk/zope.dottedname/src...

But no additional develop-egg links are present:

>>> ls('develop-eggs')
- z3c.recipe.compattest.egg-link
