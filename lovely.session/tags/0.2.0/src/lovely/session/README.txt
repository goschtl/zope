===========================
Session Data Using memcache
===========================

This package provides a session data manager which stores it's data in
memcache. The package uses lovely.memcached to store it's data.

IMPORTANT:

This test expects a memcache server running on local port 11211 which
is the default port for memcached.

This test runs in level 2 because it needs external resources to work. If you
want to run this test you need to use --all as parameter to your test.

Start a memcache instance with : memcached <optional options>


Once memcached is running, we can start testing:

  >>> from zope import component
  >>> from lovely.memcached.interfaces import IMemcachedClient
  >>> from lovely.memcached.utility import MemcachedClient
  >>> util = MemcachedClient()
  >>> component.provideUtility(util, IMemcachedClient, name='session')
  >>> util.invalidateAll()

Now we create a memcache session and connect it to the memcached client.

  >>> from lovely.session.memcached import MemCachedSessionDataContainer
  >>> sessionData = MemCachedSessionDataContainer()
  >>> sessionData.cacheName = u'session'

We need to provide a name for the session data manager because it is used to
identify the cache entry in memcache.

  >>> sessionData.__name__ = 'MemCacheSession'

  >>> session = sessionData['mySessionId']
  >>> session
  {}
  >>> type(session)
  <class 'lovely.session.memcached.MemCacheSessionData'>

We can now get data from the session.

  >>> data = session['myData']
  >>> data
  {}
  >>> type(data)
  <class 'lovely.session.memcached.MemCachePkgData'>

  >>> data['info'] = 'stored in memcache'
  >>> data
  {'info': 'stored in memcache'}



Transaction support
~~~~~~~~~~~~~~~~~~~

Because the MemCacheSession is transaction aware we need to commit the
transaction to store data in the memcache.

  >>> import transaction

  >>> transaction.commit()

If we now read session data it is read back from the memcache.

  >>> session = sessionData['mySessionId']
  >>> session['myData']
  {'info': 'stored in memcache'}

  >>> sessionData.items()
  [('mySessionId', <lovely.session.memcached.DataManager object at ...>)]


MemCacheSession is now also savepoint aware, let's check how that works:

We first set some data:

  >>> session = sessionData['mySessionId']
  >>> data = session['myData']
  >>> data['info'] = 'we want to keep this'

Set a savepoint:

  >>> savepoint = transaction.savepoint()

Change the data:

  >>> data['info'] = 'this should be dumped'

Rollback to the previous value:

  >>> savepoint.rollback()

And here it is, the before value:

  >>> data['info']
  'we want to keep this'

Newly added data must also go away:

We add a new data:

  >>> data['newinfo'] = 'go away'

And a new container:

  >>> newdata = session['myNewData']
  >>> newdata['foo'] = 'bar'

Roll it back to the previous savepoint:

  >>> savepoint.rollback()

The data is gone:

  >>> data['newinfo']
  Traceback (most recent call last):
  ...
  KeyError: 'newinfo'

The container is empty, because it gets always created on retrieval:

  >>> session['myNewData']
  {}

Let's see what happens on commit:

  >>> transaction.commit()

If we now read session data it is read back from the memcache.

  >>> session = sessionData['mySessionId']
  >>> session['myData']
  {'info': 'we want to keep this'}

The data is not present:

  >>> data['newinfo']
  Traceback (most recent call last):
  ...
  KeyError: 'newinfo'

The container is empty, because it gets always created on retrieval:

  >>> session['myNewData']
  {}
