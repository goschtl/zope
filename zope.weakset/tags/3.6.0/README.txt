Overview
========

This is the "WeakSet" implementation used by ZODB 3.6+.  It provides a
WeakSet class that implements enough of the Python set API to allow
for sets that have weakly-referenced values.

Installing This Package
=======================

Prerequisites
-------------

The installation steps below assume that you have the cool new 'setuptools'
package installed in your Python.  Here is where to get it:

  $ wget http://peak.telecommunity.com/dist/ez_setup.py
  $ /path/to/your/python ez_setup.py # req. write access to 'site-packages'

  - Docs for EasyInstall:
    http://peak.telecommunity.com/DevCenter/EasyInstall

  - Docs for setuptools:
    http://peak.telecommunity.com/DevCenter/setuptools

  - Docs for eggs:
    http://peak.telecommunity.com/DevCenter/PythonEggs


Installing a Development Checkout
---------------------------------

Check out the package from subversion:

  $ svn co svn+ssh://svn.zope.org/repos/main/Sandbox/chrism/zodb/3.6.0/zope.weakset \
    src/zope.weakset
  $ cd src/zope.weakset

Install it as a "devlopment egg":

  $ /path/to/your/python setup.py devel

Running the Tests
-----------------

Eventually, you should be able to type:

  $ /path/to/your/python setup.py test

and have it run the tests.  Today, the workaround is run the tests
from the checkout's 'weakset' directory:

  $ /path/to/your/python tests.py
    Running:
      .............
    Ran 5 tests with 0 failures and 0 errors in 0.094 seconds.

Installing a Source Distribution
--------------------------------

You can also install it from a source distribution:

  $ /path/to/easy_install --find-links="...." -eb src zope-weakset
  $ cd src/zope.weakset
  $ /path/to/your/python setup.py devel


Installing a Binary Egg
-----------------------

Install the package as a "binary egg" (which also installs its "hard"
dependencies):

  $ /path/to/easy_install --find-links="...." zope-weakset


