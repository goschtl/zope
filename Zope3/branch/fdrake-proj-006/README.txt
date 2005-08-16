Welcome to the Zope3 source

  This file provides some basic hints for people developing Zope3
  software.  There is more developer info in the Zope3 Wiki:

  http://dev.zope.org/Zope3/Zope3DeveloperInfo

  For information about the current release, see doc/CHANGES.txt.

  Zope 3 is in an early stage of development. See doc/CHANGES.txt to
  find out more!

Building and running tests

  Zope3 requires Python 2.3.4 or later.

  In the top-level Zope3 directory, you should find a script called
  setup.py.  Run it to build the extension modules needed by
  Zope.  Example::

    # cd Zope3
    # python2.3 setup.py -q build_ext -i

  On a unix variant, you can just type: 'make'

  On Windows, if you downloaded the binary distribution, this has
  already been done for you (since the compiler we use on Windows
  isn't free).

  Zope3 includes unit tests based on the Python unittest module.  If
  you check in changes, you should verify that all the tests succeed
  before you commit changes.

  To run all the tests, use the script test.py::

    # python2.3 test.py -v

  Use test.py -h for usage.  The test script can run selected tests,
  stop after the first error, run the tests in a loop, etc.

Starting Zope3

  Before running Zope, you need to create one or more bootstrap users.
  Copy the file 'sample_principals.zcml' to 'principals.zcml', and edit the
  result to your needs.  Make sure you change the passwords.

  To run Zope just run the z3.py script:

    # python2.3 z3.py

  Or, if you use make on Unix, you can run:

    # bin/runzope

  This will run Zope on port 8080.  Visit the url:

    http://localhost:8080/manage

  This goes to the Zope 3 default management interface.  Note that
  this release of Zope 3 requires recent versions of Mozilla or IE.

  If you insist on using an older browser (or a text-based browser)
  you can use the basic Zope 3 skin by putting '++skin++Basic' after
  the server part of the URL::

    http://localhost:8080/++skin++Basic/manage

  See doc/INSTALL.txt for more information.

Finding out how to develop new content types:

  We aren't as far along with documentation as we'd like to
  be.  Please be patient or help out.  Some resources:

  - The developers tutorial at:

    http://dev.zope.org/Zope3/ProgrammerTutorial

  - The Zope3 developers book at:

    http://dev.zope.org/Zope3/Zope3Book

  - Look for tidbits in the doc directory.

  - Ask questions on the mailing list, 
    http://lists.zope.org/mailman/listinfo/zope3-dev,
    or on the irc channel, #zope3-dev, on irc.openprojects.net.

  - To keep up with the latest changes, the commits mailing list
    http://lists.zope.org/mailman/listinfo/zope3-checkins

Acknowledgements

  Zope 3 is a Zope Community effort.  There are many Zope 3
  contributors without whom there wouldn't be a Zope 3.

  See the doc/CREDITS.txt file for details.

  Much thanks folks!
