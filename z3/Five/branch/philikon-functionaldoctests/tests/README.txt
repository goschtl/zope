Five tests
==========

The tests also require ZopeTestCase to be installed. ZopeTestCase can
be downloaded from here:

http://zope.org/Members/shh/ZopeTestCase

it needs to be installed in your Zope software's lib/python/Testing
directory.  Make sure you have the latest version that supports
functional doctests!

Finally, to run the tests you need to set the following environment
variables::

  export INSTANCE_HOME=/path/to/instance
  export SOFTWARE_HOME=/path/to/software/lib/python

Then you should be able to run the tests by typing::

  python2.3 runalltests.py
