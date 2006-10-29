zope.rdb Package Readme
=======================

Overview
--------

Zope RDBMS Transaction Integration.

Provides a proxy for interaction between the zope transaction framework and the
db-api connection.  Databases which want to support sub transactions need to
implement their own proxy.

Changes
-------

See CHANGES.txt.

Installation
------------

See INSTALL.txt.


Developer Resources
-------------------

- Subversion browser:

  http://svn.zope.org/zope.rdb/

- Read-only Subversion checkout:

  $ svn co svn://svn.zope.org/repos/main/zope.rdb/trunk

- Writable Subversion checkout:

  $ svn co svn+ssh://userid@svn.zope.org/repos/main/zope.rdb/trunk

- Note that the 'src/zope/rdb package is acutally a 'svn:externals' link to the
  corresponding package in the Zope3 trunk (or to a specific tag, for released
  versions of the package).
