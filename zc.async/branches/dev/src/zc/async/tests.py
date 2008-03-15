import os
import shutil
import unittest

from zope.testing import doctest, module
import zope.component
import zope.component.testing
import zope.component.eventtesting
import zc.async.interfaces
import zc.async.testing

def uuidSetUp(test):
    import zc.async.interfaces
    test.globs['old_instance_home'] = os.environ.get("INSTANCE_HOME")
    os.environ['INSTANCE_HOME'] = os.path.join(os.path.dirname(
        zc.async.interfaces.__file__), '_test_tmp')
    os.mkdir(os.environ['INSTANCE_HOME'])
    os.mkdir(os.path.join(os.environ['INSTANCE_HOME'], 'etc'))
    import zc.async.instanceuuid
    uuid = zc.async.instanceuuid.getUUID()
    if uuid != zc.async.instanceuuid.UUID: # test run changed it...
        zc.async.instanceuuid.UUID = uuid

def uuidTearDown(test):
    shutil.rmtree(os.environ['INSTANCE_HOME'])
    if test.globs['old_instance_home'] is None:
        del os.environ['INSTANCE_HOME']
    else:
        os.environ['INSTANCE_HOME'] = test.globs['old_instance_home']
    del test.globs['old_instance_home']

def modSetUp(test):
    uuidSetUp(test)
    zope.component.testing.setUp(test)
    module.setUp(test, 'zc.async.doctest_test')
    zope.component.eventtesting.setUp(test)

def modTearDown(test):
    import transaction
    transaction.abort()
    uuidTearDown(test)
    zc.async.testing.tearDownDatetime()
    module.tearDown(test)
    zope.component.testing.tearDown(test)
    if 'storage' in test.globs:
        test.globs['db'].close()
        test.globs['storage'].close()
        test.globs['storage'].cleanup()

def test_instanceuuid():
    """This module provides access to a UUID that is intended to uniquely
    identify this software instance.  Read the `msg` value below for more
    information.
    
    The uuid is generated and then stashed in a file.  It only works if
    the INSTANCE_HOME environment variable is set to a folder that has an
    `etc` folder in it--a standard Zope set up.  For this test, we mock it
    up in uuidSetUp and uuidTearDown below.
    
        >>> import zc.async.instanceuuid
        >>> import uuid
        >>> isinstance(zc.async.instanceuuid.UUID, uuid.UUID)
        True
        >>> (zc.async.instanceuuid.getUUID() ==
        ...  zc.async.instanceuuid.UUID ==
        ...  zc.async.instanceuuid.getUUID())
        True

    uuid.UUIDs now provide zc.async.interfaces.IUUID
    
        >>> import zc.async.interfaces
        >>> zc.async.interfaces.IUUID.implementedBy(uuid.UUID)
        True
        >>> zc.async.interfaces.IUUID.providedBy(zc.async.instanceuuid.UUID)
        True

    That's a bit invasive, but now you can register the instance UUID as
    a utility and get it back out as something that provides
    zc.async.interfaces.IUUID.
    
        >>> import zope.component
        >>> zope.component.provideUtility(
        ...     zc.async.instanceuuid.UUID, name='instance')
        >>> id = zope.component.getUtility(
        ...     zc.async.interfaces.IUUID, 'instance')
        >>> id is zc.async.instanceuuid.UUID
        True

    (Unfortunately you can't register a utility to provide a class, or I
    would have done that...though maybe that's not unfortunate :-) )

    """
def test_long_to_dt():
    """The utils module provides two cool methods to convert a date to a long
    and back again.  Dates in the future get smaller and smaller, so dates
    are arranged from newest to oldest in a BTree.  It leaves an extra 4 bits
    at the bottom.  It can convert all possible datetimes.
    
    >>> from zc.async.utils import long_to_dt, dt_to_long
    >>> import datetime
    >>> now = datetime.datetime.now()
    >>> isinstance(dt_to_long(now), long)
    True
    >>> now == long_to_dt(dt_to_long(now))
    True
    >>> now == long_to_dt(dt_to_long(now)+15)
    True
    >>> datetime.datetime.max == long_to_dt(dt_to_long(datetime.datetime.max))
    True
    >>> CE = datetime.datetime(1,1,1)
    >>> CE == long_to_dt(dt_to_long(CE))
    True
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=uuidSetUp, tearDown=uuidTearDown),
        doctest.DocFileSuite(
            'job.txt',
            'jobs_and_transactions.txt',
            'queue.txt',
            'agent.txt',
            'dispatcher.txt',
            'README.txt',
            setUp=modSetUp, tearDown=modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
