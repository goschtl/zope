Overview
========

This package is obsolete and its functionality has been merged into the ZODB3
distribution itself. If you use version 3.10 or later of ZODB3, please change
your imports of the IBroken interface to a direct::

  from ZODB.interfaces import IBroken

You can use this package with older versions of the ZODB3, which didn't have
the IBroken interface yet.
