"""
======================
Testing XML-RPC access
======================

First we setup the app and XML-RPC proxy::

  >>> from grok.ftests.xmlrpc_helper import ServerProxy
  >>> from kirbi.app import Kirbi
  >>> root = getRootFolder()
  >>> root['kirbi'] = Kirbi()
  >>> server = ServerProxy("http://localhost/kirbi/pac")

Now we use the proxy to add books::

  >>> server.add(dict(title="One Flew Over the Cuckoo's Nest"))
  'k0001'
  >>> server.add(dict(isbn13='9780684833392'))
  '9780684833392'
  >>> server.add(dict(isbn13='9780486273471'))
  '9780486273471'
  >>> server.add(dict(title=u'Utopia', isbn13='9780140449105'))
  '9780140449105'
  >>> sorted(server.list())
  ['9780140449105', '9780486273471', '9780684833392', 'k0001']

The second and third books added have ISBN but no title, so they are added to
the pending dict for remote metadata fetching::

  >> sorted(server.list_pending_isbns())
  ['9780486273471', '9780684833392']

The fetch script can remove pending ISBNs (the number of ISBNs actually
removed is returned)::

  >> server.delPending(['9780684833392','9780486273471','not-an-isbn'])
  999
  >> sorted(server.list_pending_isbns())
  []


"""
