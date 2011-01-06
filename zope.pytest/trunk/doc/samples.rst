Examples
========

We can import stuff from zope.pytest:

  >>> from zope.pytest import configure
  >>> a=1

We can run py.test for instance like this:

  >>> import os
  >>> import zope.pytest
  >>> zopepytest_dir = os.path.dirname(zope.pytest.__file__)

  >>> import pytest
  >>> pytest.main("%s" % zopepytest_dir)
  =====... test session starts ...======
  platform ...
  collecting ...
  collected 2 items
  ...
  =====... 2 passed in ... seconds ...=====
  ...

Just an example. We can test this output via the doctest-builder.

Check, whether complete setup fixtures can be tested this way.

