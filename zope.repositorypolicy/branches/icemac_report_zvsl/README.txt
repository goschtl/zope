Rules enforced by ``zope.repositorypolicy``
===========================================


This package provides a ``zope-org-check-project`` script that is run
nightly against the zope.org Subversion repository. The script checks the
rules below against all top level subversion projects, with the
exception of ``Sandbox``.  For each project, the script checks the ``trunk``
(if it exists), the ``develop`` branch (if it exists), and any "release"
branches matching the pattern ``branches/{major}.{minor}``, where ``major``
and ``minor`` are integers.

The script ignores releases of a project (typically in
``tags/{major}.{minor}.{patch}``).  New releases for a project should be made
from a branch, or the trunk, only after bringing that branch into conformance.


Copyright and License Rules
---------------------------

- Any module which contains a copyright header (c-style, python style, or
  otherwise) must indicate that the copyright belongs to "Zope Foundation
  and Contributors."  The phrase "All Rights Reserved" is not requried.
  Existing copyright dates should be preserved when changing the copyright
  holder.

- Every checked project branch must contain a file named, "LICENSE.txt"
  which contains the canonical copy of the ZPL 2.1 license.  As of 2010-05-09,
  the checker requires that this file match its canonical version exactly.

- Every checked project branch must contain a file named "COPYRIGHT.txt"
  which indicates that the copyright belongs to the foundation.  This file
  must not contain any language or information other than the following::
   
     Zope Foundation and Contributors

- If a checked project branch contains a ``setup.py`` file for consumption
  by ``distutils`` or other related tools, each call into the ``setup()``
  API must include the ``license`` keyword argument, with the string
  "ZPL" or "ZPL 2.1" as the value.  E.g::

     from setuptools import setup
     setup(name='somepackage',
           version='1.2',
           description='A description',
           license='ZPL 2.1',
           ...
          )


Conformance
-----------

Most project branches should be easy to bring into conformance.  The
``zope-org-check-project`` script provided by this package will find and
report on violations.  E.g.::

  $ bin/zope-org-check-project /path/to/someproject
  LICENSE.txt: Missing license file
  COPYRIGHT.txt: Missing copyright file
  src/someproject/adapters.py:3: incorrect copyright holder: Zope Corporation and Contributors
  ...

The ``zope-org-fix-project`` file can fix all the copyright headers, as well
as adding the missing required files.  E.g.::

  $ bin/zope-org-check-project /path/to/someproject
  $ bin/zope-org-fix-project /path/to/someproject
  $ svn stat /path/to/someproject
  ? LICENSE.txt
  ? COPYRIGHT.txt
  M src/someproject/adapters.py
  ...

**N.B.**
    Don't forget to add the newly-generated boilerplate files before checking
    in the changes.


Non-Conforming Projects
-----------------------

If any portion of the project cannot be conformed to these guidelines (e.g.
because some file or part of a file is under copyright to a non-committer),
one of the following remedies must be applied.

- Move the project from the zope.org repository to a different code hosting
  site.

- Remove the non-ZPL-licensed files from the project, perhaps documenting
  how a user can restore them at installation time.

- Apply to the Zope Foundation board for an exception to the policy.  Once
  granted, the exempted project branches must contain a file, "EXEMPTIONS.txt",
  containing the date and scope of the exemption.  The "LICENSE.txt" and
  "COPYRIGHT.txt" files should be amended to indicate the portions of code
  which are under a different license, or copyright.  Project branches
  containing the "EXEMPTIONS.txt" file will be skipped by the
  ``zope-org-check-repository`` script when running the nightly conformance
  report.

