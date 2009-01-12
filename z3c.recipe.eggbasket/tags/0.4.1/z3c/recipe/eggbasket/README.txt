Goal of this recipe
===================

You have an egg (for example ``grok``) that has a lot of dependencies.
Other eggs that it depends on are found on the cheeseshop, on
sourceforge, and perhaps on some more servers.  When even one of these
servers is down, other people (or you yourself) cannot install that
egg.  Or perhaps your egg depends on a specific version of another egg
and that version is removed from the cheeseshop for some bad reason.

In other words: there are multiple points of failure.  Interested
users want to try your egg, the install fails because a server is
down, they are disappointed, leave and never come back.

The goal of this recipe is to avoid having those multiple points of
failure.  You create a tarball containing all eggs that your egg
depends on.  A package like zc.sourcerelease_ can help here, but our
recipe can also create such a tar ball.  Include it in a buildout like
this::

  [buildout]
  parts = bundlemaker

  [bundlemaker]
  recipe = z3c.recipe.eggbasket:creator
  egg = grok
  versionfile = http://grok.zope.org/releaseinfo/grok-0.12.cfg

After you have made that tar ball, you need to upload it somewhere.
In your buildout you point this recipe to your egg and the url of the
tarball, for example like this::

  [buildout]
  parts = eggbasket

  [eggbasket]
  recipe = z3c.recipe.eggbasket
  eggs = grok
  url = http://grok.zope.org/releaseinfo/grok-eggs-0.12.tgz

The part using this recipe should usually be the first in line.  What
the recipe then does is install your egg and all its dependencies
using only the eggs found in that tarball.  After that you can let the
rest of the buildout parts do their work.

.. _zc.sourcerelease: http://pypi.python.org/pypi/zc.sourcerelease


Limitations
===========

1. This approach still leaves you with multiple points of failure:

   - the cheeseshop must be up so the end user can install this recipe

   - the server with your tarball must be up.

2. Before buildout calls the install method of this recipe to do the
   actual work, all buildout parts are initialized.  This means that
   all eggs and dependencies used by all recipes are installed.  This
   can already involve a lot of eggs and also multiple points of
   failure.  Workaround: you can first explicitly install the part
   that uses this recipe.  So with the buildout snippet from above
   that would be::
   
     bin/buildout install eggbasket


Supported options
=================

The recipe supports the following options:

eggs
    One or more eggs that you want to install with a tarball.

url
    Url where we can get a tarball that contains the mentioned eggs
    and their dependencies.


The releasemaker script supports the following options:

egg
    The main egg that we want to bundle up with its dependencies.
    This is required.

versionfile
    Config file that contains the wanted versions of the main egg and
    its dependencies.  An example is the grok version file:
    http://grok.zope.org/releaseinfo/grok-0.12.cfg
    This file is parsed by zc.buildout, so you can for example extend
    other files.  And the file can be a url or the name of a file in
    the current directory.


Example usage
=============

We have a package ``orange`` that depends on the package ``colour``::

    >>> import os.path
    >>> import z3c.recipe.eggbasket.tests as testdir
    >>> orange = os.path.join(os.path.dirname(testdir.__file__), 'orange')
    >>> colour = os.path.join(os.path.dirname(testdir.__file__), 'colour')

We create source distributions for them in a directory::

    >>> colours = tmpdir('colours')
    >>> sdist(orange, colours)
    >>> sdist(colour, colours)
    >>> ls(colours)
    -  colour-0.1.zip
    -  orange-0.1.zip

We will define a buildout template that uses the recipe::

    >>> buildout_template = """
    ... [buildout]
    ... parts = basket
    ...
    ... [basket]
    ... recipe = z3c.recipe.eggbasket
    ... eggs = %(eggs)s
    ... url = %(url)s
    ... """

We'll start by creating a buildout that does not specify an egg::

    >>> write('buildout.cfg', buildout_template % { 'eggs': '', 'url' : 'http://nowhere'})

In this case the recipe will do nothing.  So the url does not get
used.  Running the buildout gives us::

    >>> print system(buildout)
    ...
    Installing basket.
    <BLANKLINE>

Next we will specify an egg but refer to a bad url::

    >>> write('buildout.cfg', buildout_template % { 'eggs': 'orange', 'url' : 'http://nowhere'})
    >>> print system(buildout)
    Uninstalling basket.
    Installing basket.
    Couldn't find index page for 'orange' (maybe misspelled?)
    Getting distribution for 'orange'.
    basket: Distributions are not installed. A tarball will be downloaded.
    basket: Downloading http://nowhere ...
    basket: Url not found: http://nowhere.
    <BLANKLINE>

So now we create a tar ball in a directory::

    >>> import tarfile
    >>> tarserver = tmpdir('tarserver')
    >>> cd(tarserver)
    >>> tarball = tarfile.open('colours.tgz', 'w:gz')
    >>> tarball.add(colours)

Note: the order of the next listing is not guaranteed, so there might
be a test failure here:

    >>> tarball.list(verbose=False)
    tmp/tmpDlQSIQbuildoutSetUp/_TEST_/colours/
    tmp/tmpDlQSIQbuildoutSetUp/_TEST_/colours/orange-0.1.zip
    tmp/tmpDlQSIQbuildoutSetUp/_TEST_/colours/colour-0.1.zip
    >>> tarball.close()
    >>> ls(tarserver)
    -  colours.tgz

We make it available on a url and use it in our buildout::

    >>> cd(sample_buildout)
    >>> tarball_url = 'file://' + tarserver + '/colours.tgz'
    >>> write('buildout.cfg', buildout_template % { 'eggs': 'orange', 'url' : tarball_url})
    >>> print system(buildout)
    Uninstalling basket.
    Installing basket.
    Couldn't find index page for 'orange' (maybe misspelled?)
    Getting distribution for 'orange'.
    basket: Distributions are not installed. A tarball will be downloaded.
    basket: Downloading .../tarserver/colours.tgz ...
    basket: Finished downloading.
    basket: Extracting tarball contents...
    basket: Installing eggs to .../sample-buildout/eggs which will take a while...
    Getting distribution for 'orange'.
    ...
    Got orange 0.1.
    Getting distribution for 'colour'.
    ...
    Got colour 0.1.
    <BLANKLINE>
