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
depends on.  A package like zc.sourcerelease_ can help here. You
upload that tarball somewhere.  In your buildout you point this recipe
to your egg and the url of the tarball, for example like this::

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


Example usage
=============

.. Note to recipe author!
   ----------------------
   zc.buildout provides a nice testing environment which makes it
   relatively easy to write doctests that both demonstrate the use of
   the recipe and test it.
   You can find examples of recipe doctests from the PyPI, e.g.
   
     http://pypi.python.org/pypi/zc.recipe.egg

   The PyPI page for zc.buildout contains documentation about the test
   environment.

     http://pypi.python.org/pypi/zc.buildout#testing-support

   Below is a skeleton doctest that you can start with when building
   your own tests.

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = z3c.recipe.eggbasket
    ... option1 = %(foo)s
    ... option2 = %(bar)s
    ... """ % { 'foo' : 'value1', 'bar' : 'value2'})

Running the buildout gives us::

    >>> print system(buildout)
    Installing test1.
    Unused options for test1: 'option2' 'option1'.


