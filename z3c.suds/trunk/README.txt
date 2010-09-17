Introduction
============

z3c.suds manages a connection pool of `suds`_ client objects in the context of
a ZODB-based application.  (suds is a lightweight client library for consuming
SOAP web services in Python.)  Using it avoids the need for instantiating a new
client for the same webservice in multiple requests (which may be expensive due
to parsing WSDL, etc.)

.. _`suds`: https://fedorahosted.org/suds/

Usage
-----

A client may be obtained via the `get_suds_client` method::

  client = get_suds_client(wsdl_uri, context=None)

This returns an existing suds client if one is found in the cache for the given
WSDL; otherwise it returns a new client object and stores it in the cache.

`wsdl_path` is the URI of the WSDL (web service definition language)
description of the web service. (Use a file:// URI for a locally stored WSDL.)

`context` is a persistent object (in the ZODB sense). If not provided, the
`getSite` method of zope.site.hooks will be used to obtain an object (which
is probably only sensible within the context of a Zopish framework). If the
context object is associated with a ZODB connection, the client will be cached
in the connection's `foreign_connections` dictionary. If the context object is
not yet associated with a ZODB connection, the client will be cached in a
volatile attribute instead. This approach to piggybacking a pool of connections
on the ZODB connection pool is based on `alm.solrindex`, and further documented
there.

.. _`alm.solrindex`: http://pypi.python.org/pypi/alm.solrindex

