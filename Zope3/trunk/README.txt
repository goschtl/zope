Welcome to the Zope3 source

  This file provides some basic hints for people developing Zope3
  software.  There is more developer info in the Zope3 Wiki:

  http://dev.zope.org/Zope3/Zope3DeveloperInfo

  For information about the current release, see CHANGES.txt.

  Zope 3 is in an early stage of development. See CHANGES.txt to find
  out more!

Building and running tests

  Zope3 requires Python 2.2.3 or later and PyXML 0.8.1 or higher.
  PyXML can be downloaded from http://sf.net/projects/pyxml.

  In the top-level Zope3 directory, you should find a script called
  setup.py.  Run it to build the extension modules needed by
  Zope.  Example::

    # cd Zope3
    # python2.2 setup.py -q build_ext -i

  On a unix variant, you can just type: make

  On Windows, if you downloaded the binary distribution, this has
  already been done for you (since the compiler we use on Windows
  isn't free).

  Zope3 includes unit tests based on the Python unittest module.  If
  you checkin changes, you should verify that all the tests succeed
  before you checkin.

  To run all the tests, use the script test.py::

    # python2.2 test.py -v

  Use test.py -h for usage.  The test script can run selected tests,
  stop after the first error, run the tests in a loop, etc.

Starting Zope3

  Before running Zope, you need to create one or more bootstrap
  users. Try copying and editing the file sample_principals.zcml to
  principals.zcml.  Make sure you change the passwords.

  To run Zope just run the z3.py script:

    # python2.2 z3.py

  This will run Zope on port 8080.  Visit the url:

    http://localhost:8080/manage

  This will access the Zope 3 default management interface.  Note that
  this release of Zope 3 requires recent versions of Mozilla or IE.

  If you insist on using an older browser (or a text-based browser)
  you can use the basic Zope 3 skin by putting '++skin++basic' after
  the server part of the URL::

    http://localhost:8080/++skin++basic/manage

  Copy principals.zcml.in to principals.zcml, and add a manager
  entry to it based on the examples in sample_principals.zcml.

  see doc/INSTALL for more information

Finding out how to develop new content types:

  We aren't as far along with documentation as we'd like to
  be. Please be patient or help out. Some resources.

  - The developers tutorial at:

    http://dev.zope.org/Zope3/ProgrammerTutorial

  - The Zope3 developer cookbook at:

    http://dev.zope.org/Zope3/DevelCookbook

  - Look for tidbits in the doc directory.

  - Ask questions on the mailing list, 
    http://lists.zope.org/mailman/listinfo/zope3-dev,
    or on the irc channel, #zope3-dev, on irc.openprojects.net.

  - To keep up with the latest changes, the cvs-commit mailing list
    http://lists.zope.org/mailman/listinfo/zope3-checkins

Acknowledgements

  Zope 3 is a Zope Community effort.  There are many Zope 3
  contributors without whom there wouldn't be a Zope 3.

  See the doc/CREDITS.txt file for details.

  Much thanks folks!
