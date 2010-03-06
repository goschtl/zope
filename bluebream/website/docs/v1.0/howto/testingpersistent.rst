Testing persistent objects
==========================

.. based on http://www.mail-archive.com/zope3-users@zope.org/msg03555.html

You can create a fake module to test persistent objects with
transaction commits, otherwise you will get an error like this::

  PicklingError: Can't pickle <class 'TestItem'>: attribute lookup __builtin__.TestItem failed

This HOWTO explain creating fake module to write test cases.  The
functionality to create fake module is provided by
``zope.testing.module``.

Inside your ticket collector application, you can create a
``persistent_test.txt`` file with a test case like this::

  :doctest:

  >>> from ZODB.tests.util import DB
  >>> import transaction
  >>> db = DB()
  >>> conn = db.open()
  >>> root = conn.root()

  >>> from persistent import Persistent

  >>> class TestItem(Persistent):
  ...     pass

  >>> item = TestItem()
  >>> root['item'] = item
  >>> transaction.commit()

Now invoke the test runner as given below::

  $ ./bin/test

You should get an erorr like this::

  PicklingError: Can't pickle <class 'TestItem'>: attribute lookup __builtin__.TestItem failed

Now open the ``tests.py`` and add two keyword arguments to
``z3c.testsetup.register_all_tests`` function named ``setup`` and
``teardown``.  The values of those keyword arguments could be
``zope.testing.module.setUp`` and ``zope.testing.module.tearDown``
respectively as given here::

  from zope.testing import module
  test_suite = z3c.testsetup.register_all_tests('testp2.main', setup=module.setUp, teardown=module.tearDown)

A better method would be to create your own ``setUp`` and
``tearDown`` functions as given below so that you can add more code
there, if required.  Here is custom ``setUp`` and ``tearDown``
without any extra code::

  import z3c.testsetup
  from zope.testing import module

  def setUp(test):
      module.setUp(test)

  def tearDown(test):
      module.tearDown(test)

  test_suite = z3c.testsetup.register_all_tests('testp2.main', setup=setUp, teardown=tearDown)


By default the fake module name will be ``__main__``.  If you require
another name for the module, you can specify it like this::

   module.setUp(test, 'mymodule')
   module.tearDown(test, 'mymodule')

Now you can import the ``mymodule`` from the test cases
(``persistent_test.txt``).  Based on this module name functionality,
here is a better way to create ``setUp`` and ``tearDown``::

  import z3c.testsetup
  from zope.testing import module

  module_name = 'testp2.main.mypersistent'

  def setUp(test):
      module.setUp(test, module_name)

  def tearDown(test):
      module.tearDown(test, module_name)

  test_suite = z3c.testsetup.register_all_tests('testp2.main', setup=setUp, teardown=tearDown)
