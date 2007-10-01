==============
z3c.recipe.egg
==============

Recipes based on zc.recipe.egg for working with source
distributions.

Editable Distributions
----------------------

The z3c.recipe.egg:editable recipe uses the easy_install --editable
and --build-directory options to download multiple source
distributions.

The source distributions will be placed in the part directory and
managed by the buildout if build-directory is not specified.  If so,
the distributions will be replaced when newer versions are available.
So be sure to set build-directory to a directory not managed by
buildout if you want to maintain changes to the source distributions.

The z3c.recipe.egg:editable can be used to assemble a set of
subversion checkouts to work with specifying subversion URLs in
find-links as is supported by easy_install.  See the easy_install
documentation for the syntax for using subversion URLs.  There are a
number of ways in which it is more flexible to control checkouts via
recipes rather than svn:externals.

Finally, if the develop option is true then the distributions will be
installed in develop mode.

See z3c/recipe/egg/editable.txt for more details.

Running Setup Scripts
---------------------

The z3c.recipe.egg:setup recipe calls arbitrary setup.py commands on
multiple distributions in a buildout.

The z3c.recipe.egg:setup recipe can be used, for example, to automate
releases.  When the source is ready for release, the setup recipe is
configured to run the "register sdist bdist_egg upload" setup
commands.  To ensure release only runs when intended, the setup recipe
can be used in it's own release.cfg file that extends
the buildout.cfg file.  With this setup, releases for multiple
projects can be made with "bin/buildout -c release.cfg".

The z3c.recipe.egg:setup recipe also supports the develop option as
with z3c.recipe.egg:editable.

See z3c/recipe/egg/setup.txt for more details.
