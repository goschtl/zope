===================
Zope Packaging Tool
===================

This is a *prototype* packaging tool; we hope it will evolve into
something general and useful, but is still somewhat specialized and
undercooked at this time.  This is initially targetted at supporting
the creation of Zope 3 releases.

The "zpkg" script in the bin/ directory is the command line tool that
ise used to generate a package from source information.  Most of the
implementation is stored in the ``zpkgtools`` Python package.

Additional discussion related to the goals and design of this tool can
be found in the Zope 3 wiki:

  http://dev.zope.org/Zope3/Zope3PackagingProposal
