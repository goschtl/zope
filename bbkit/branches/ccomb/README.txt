BlueBream Kit
=============

The BlueBream Kit consists a set of packages used by the BlueBream
project.  BlueBream Kit (**bbkit**) is part of the BlueBream project
infrastructure.

- The Kit will provide a place holder location for KGS based release
  tagging and maintenance

- The Kit will help to perform compatibility tests for supported
  packages

- Categorize packages and define the status of each package

- Provide multiple package lists based on the category & status

For development progress of this package, see this wiki:
http://wiki.zope.org/bluebream/BlueBreamKit

Package categories
------------------

- Core (ZTK & ZopeApp packages defined in zopetoolkit)
- Community (z3c.* and other community maintained packages)
  Community packages are suported by community.

Runnig compatibility test suite
-------------------------------

::

 $ python bootstrap.py
 $ ./bin/buildout
 $ ./bin/test-ztk
 $ ./bin/test-zopeapp
 $ ./bin/test-community

