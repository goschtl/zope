Zope 3 Checkout
===============

Recipe for creating a Zope 3 checkout in a buildout.

Hopefully, when Zope is packaged as eggs, this won't be necessary.

The recipe has a single option, which is the Subversion URL to use to
checkout Zope.  For example, to get the 3.3 branch, use:

   url = svn://svn.zope.org/repos/main/branches/3.3

The checkout is installed into a subdirectory of the buildout parts
directory whose name is the part name used for the recipe.

This location is recorded in a 'location' option within the section
that other recipes can query to get the location.
