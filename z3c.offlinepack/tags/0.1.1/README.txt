;-*- rST -*-

==================
Pack ZODBs Offline
==================

Pack a ZODB storage without running any part of the Zope application
server.  Only an appropriate version of Zope for the ZODB storage is
required.  Use on a copy of a ZODB storage.  Do not run on a ZODB
storage currently in use.

Install the distribution:

  $ python setup.py install

Then use the offlinepack script to pack a copy of your ZODB:

  $ offlinepack /path/to/Data-copy.fs

zc.buildout
-----------

A buildout.cfg is included that will install the offlinepack script
to the buildout.  The buildout makes it possible to quickly use the
offlinepack script without modifying your python installation.

  $ python bootsrtap/bootsrtap.py -v
  $ bin/buildout -v
  $ bin/offlinepack /path/to/Data-copy.fs

The buildout.cfg file can also be modified to use a specific version
of ZODB3.  This is uesful if you need to use offlinepack without
migrating the ZODB to a newer version of ZODB3.  Add the version
specifier to the offlinepack section of buildout.cfg.  For example, to
use offlinepack with Zope 2.9, use the following offlinepack section.

    [offlinepack]
    recipe = zc.recipe.egg:scripts
    eggs = z3c.offlinepack
        ZODB3<3.7-dev
