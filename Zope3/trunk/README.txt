Welcome to the Zope3 source

  The file provides some basic hints for people developing Zope3
  software.  There is more developer info in the Zope3 Wiki:
  http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/
  Zope3DeveloperInfo

  That's one URL split over two lines.

Building and running tests

  Zope3 requires Python 2.2

  In the top-level Zope3 directory, you should find a script called
  stupid_build.py.  Run it to build the extension modules needed by
  Zope.  Example:

  # cd src/Zope3
  # python2.2 stupid_build.py

  Zope3 includes unit tests based on the Python unittest module.  If
  you checkin changes, you should verify that all the tests succeed
  before you checkin.

  To run all the tests, use the script test.py.
  # python test.py -v

  Use test.py -h for usage.  The test script can run selected tests,
  stop after the first error, run the tests in a loop, etc.
