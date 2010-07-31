docs.zope.org buildout README
=============================
This buildout automates building content for the docs.zope.org 
website. It uses the ``dataflake.docbuilder`` package to do the 
following:

* Define pages showing sets of software packages
* Download and build `Sphinx` documentation for these packages
* Link the resulting package documentation in one central place
* Build an index file showing the documented packages


How do remove a package from a package list?
--------------------------------------------
Find the respective buildout stanza and remove the 
Subversion URL in the ``sources`` list.  Afterwards run 
``bin/buildout`` to regenerate the documentation build 
scripts for the stanzas you changed and re-run them.


How do I add a package to a package list?
-----------------------------------------
If your newly added package has a standard Sphinx setup with 
a ``doc`` or ``docs`` folder in the package root containing 
the `Sphinx` documentation and configuration then this is 
easy. Find the respective buildout stanza and add the Subversion
URL to the list of URLs in ``sources``.  The URL must use 
a protocol understood by Subversion, and it must point to 
the main package location which has the package's 
``trunk`` folder in it.

If your new package relies on the ``z3c.recipe.sphinxbuild``
way of doing things it's a little more complicated. You should 
consider converting it to the standard setup described above 
with documentation and a Sphinx configuration stored in the 
package root.

First, you need to visit the ``z3c.recipe.sphinxbuild`` buildout 
configuration at ``/home/zope/z3c.sphinxdocs``. Add your package 
name to its buildout configuration, following the conventions 
for the other packages. Make sure you create a trunk checkout 
of your package underneath ``/home/zope/z3c.sphinxdocs`` 
as well. Then re-run ``bin/buildout`` and ``bin/docs`` to build
the documentation.

When your ``z3c.recipe.sphinxbuild``-based documentation is built 
you can add the package URL to the site buildout as explained in 
the first paragraph.

When you're done changing the buildout configuration re-run
``bin/buildout`` to regenerate the documentation build 
scripts for the stanzas you changed and re-run them.


How do I add another packages set page?
---------------------------------------
Start by copying an existing buildout stanza. Then change 
the values for ``index-name`` (this is the page name for
your package list without any extension like ``.rst``), 
and the Subversion URLs in the ``sources`` list.

The main site index is built from the file ``templates/index.rst`` 
and should be maintaind by hand. Simply add another section or 
link as needed for your new package set page and rebuild.

When you're done changing the buildout configuration re-run
``bin/buildout`` to generate the documentation build scripts for 
the stanzas you added and run them.


How do I change the site styling or layout?
-------------------------------------------
The site root is built from the Sphinx configuration in 
the ``templates`` folder. You can adjust the main page content 
(the ``index.rst`` file) and the configuration as you like.

