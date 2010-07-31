docs.zope.org buildout README
=============================
This buildout automates building content for the docs.zope.org 
website. It uses the ``dataflake.docbuilder`` package to do the 
following:

* Define pages showing sets of software packages
* Download and build `Sphinx` documentation for these packages
* Link the resulting package documentation in one central place
* Build an index file showing the documented packages


How do I add or remove a package from a package list?
-----------------------------------------------------
Find the respective buildout stanza and remove or add the 
Subversion URLs in the ``sources`` list. The URL must use 
a protocol understood by Subversion, and it must point to 
the `main` package location which has the package's 
``trunk`` folder in it.


How do I add another packages set page?
---------------------------------------
Start by copying an existing buildout stanza. Then change 
the values for ``index-name`` (this is the page name for
your package list without any extension like ``.rst``), 
and the Subversion URLs in the ``sources`` list.

The main site index is built from the file ``templates/index.rst`` 
and should be maintaind by hand. Simply add another section or 
link as needed for your new package set page and rebuild.


How do I change the site styling or layout?
-------------------------------------------
The site root is built from the Sphinx configuration in 
the ``templates`` folder. You can adjust the main page content 
(the ``index.rst`` file) and the configuration as you like.
