zope.tal Package Readme
=======================

Overview
--------

The Zope3 Template Attribute Languate (TAL) specifies the custom namespace
and attributes which are used by the Zope Page Templates renderer to inject
dynamic markup into a page.  It also includes the Macro Expansion for TAL
(METAL) macro language used in page assembly.

The dynamic values themselves are specified using a companion language,
TALES (see the 'zope.tales' package for more).

See: http://www.zope.org/Wikis/DevSite/Projects/ZPT/TAL%20Specification%201.4

Changes
-------

See CHANGES.txt.

Installation
------------

See INSTALL.txt.


Developer Resources
-------------------

- Subversion browser:

  http://svn.zope.org/zope.tal/

- Read-only Subversion checkout:

  $ svn co svn://svn.zope.org/repos/main/zope.tal/trunk

- Writable Subversion checkout:

  $ svn co svn://svn.zope.org/repos/main/zope.tal/trunk

- Note that the 'src/zope/tal' package is acutally a 'svn:externals' link
  to the corresponding package in the Zope3 trunk (or to a specific tag,
  for released versions of the package).
