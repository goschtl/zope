Welcome to the Zope3 source

  This file provides some basic hints for people developing Zope3
  software.  There is more developer info in the Zope3 Wiki:

  http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/Zope3DeveloperInfo

  For information about the current release, see CHANGES.txt.

  Zope 3 is in an early stage of development. See CHANGES.txt to find
  out more!

Building and running tests

  Zope3 requires Python 2.2.2 or later.

  In the top-level Zope3 directory, you should find a script called
  setup.py.  Run it to build the extension modules needed by
  Zope.  Example:

  # cd Zope3
  # python2.2 setup.py -q build_ext -i

  On a unix variant, you can just type: make

  Zope3 includes unit tests based on the Python unittest module.  If
  you checkin changes, you should verify that all the tests succeed
  before you checkin.

  To run all the tests, use the script test.py.
  # python test.py -v

  Use test.py -h for usage.  The test script can run selected tests,
  stop after the first error, run the tests in a loop, etc.

Finding out how to develop new content types:

  We aren't as far along with documentatoion as we'd like to
  be. Please be patient or help out.

  - See the developers tutorial at:

    http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/ProgrammerTutorial

  - Look for tidbits in the doc directory.

  - Ask questions on the mailing list, 
    http://lists.zope.org/mailman/listinfo/zope3-dev,
    or on the irc channel, #zope3-dev, on irc.openprojects.net.

Acknowledgements

  Zope 3 is a Zope Community effort.  There are many Zope 3
  contributors without whom there wouldn't be a Zope 3.

  See the doc/CREDITS.txt file for details.

  Much thanks folks!
