Five tests
==========

The tests require ZopeTestCase to be installed. ZopeTestCase can be
downloaded from here:

http://zope.org/Members/shh/ZopeTestCase

It needs to be installed in your Zope software's lib/python/Testing
directory.

To run the tests, all you have to do is type::

  ./bin/zopectl test --dir Products/Five

to run the Five tests. For older versions of Zope you need to set the
following environment variables::

  export INSTANCE_HOME=/path/to/instance
  export SOFTWARE_HOME=/path/to/software/lib/python
