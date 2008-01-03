************
ZODB Recipes
************

Recipes for working with ZODB.

Changes
*******

0.3 (2008-01-03)
================

New Features
------------

- You can now specify an email address in a packing crontab file to
  control where errors are sent.

- If you install a general ZEO script, using a zdaemon part::

    [zdaemon]
    recipe = zc.recipe.egg:script
    eggs = zdaemon

  you can request that shell scripts be generated that use the generic
  zdaemon script. This can make updating software for deployed systems
  easier since instance-specific scripts don't depend on paths, like
  egg names, that are likely to change.

Bugs Fixed
----------

- ZODB3 and most of its requirements were spurious dependencies of the
  recipes. This caused ZODB3 to be installed using the Python used to
  run the buildout, which caused problems in some circumstances.

0.2.1 (2007-04-23)
==================

Bugs Fixed
----------

- crontab and logrotate configuration files were being generates incorrectly.

0.2 (2007-04-17)
================

Added handling of %import directives.

0.1 (2007-04-13)
================

Initial release.

.. contents::
