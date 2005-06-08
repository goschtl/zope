===================
Zope Packaging Tool
===================

This is a *prototype* packaging tool; we hope it will evolve into
something general and useful, but is still somewhat specialized and
undercooked at this time.  This is initially targetted at supporting
the creation of Zope 3 releases.

The "zpkg" script in the bin/ directory is the command line tool that
is used to generate a package from source information.  Most of the
implementation is stored in the ``zpkgtools`` Python package.

Documentation for this software can be found in the doc/ directory.
The reStructuredText documents can be read directly or converted to
HTML (see doc/Makefile); doc/index.txt (or doc/index.html) provides an
overview of the available documentation and links to related material.

Additional discussion related to the goals and design of this tool can
be found in the Zope 3 wiki:

  http://dev.zope.org/Zope3/Zope3PackagingProposal

An online version of the documentation is available at:

  http://www.zope.org/Members/fdrake/zpkgtools/


Running the unit tests
----------------------

There are unit tests of the zpkgtools package in the zpkgtools.tests
package.  This can most easily be run by running the *test.py* script
found in the same directory as this README.txt file::

  $ python2.3 tests.py
  ......................................................................
  ......................................................................
  ........................................
  ----------------------------------------------------------------------
  Ran 197 tests in 0.931s

  OK


Reporting Bugs
--------------

Bugs in this package should be reported in the Zope 3 collector:

  http://collector.zope.org/Zope3-dev/
