Zope 3 Checkout
===============

Recipe for creating a Zope 3 checkout in a buildout.

Hopefully, when Zope is packaged as eggs, this won't be necessary.

The recipe has two options:

- The Subversion URL to use to checkout Zope. For example, to get the 3.3
  branch, use:

   url = svn://svn.zope.org/repos/main/branches/3.3

  This option is required.

- The revision to check out. This is optional and defaults to "HEAD".

The checkout is installed into a subdirectory of the buildout parts
directory whose name is the part name used for the recipe.

This location is recorded in a 'location' option within the section
that other recipes can query to get the location.
