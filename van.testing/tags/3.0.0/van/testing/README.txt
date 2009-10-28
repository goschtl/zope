van.testing provides tools for testing zope3/WSGI based applications that do
not use the ZODB or local utilities.

Testing Utilities
-----------------

The most common use of this testing module is functional testing zope
applications. It provides tools to setup layers which load the configuration
ZCML as well as setting up wsgi_intercept in a layer.

This test is part of such a layer (setup in van.testing.tests.FunctionalLayer):

    >>> from wsgi_intercept import WSGI_HTTPConnection as HTTPConnection
    >>> conn = HTTPConnection('localhost', 80)

    >>> conn.request('GET', '/')
    >>> r = conn.getresponse()
    >>> print r.read() # doctest: +ELLIPSIS
    {'HTTP_ACCEPT_ENCODING': 'identity',
     'HTTP_HOST': 'localhost',
     'PATH_INFO': '/',
     'QUERY_STRING': '',
     'REMOTE_ADDR': '127.0.0.1',
     'REQUEST_METHOD': 'GET',
     'SCRIPT_NAME': '',
     'SERVER_NAME': 'localhost',
     'SERVER_PORT': '80',
     'SERVER_PROTOCOL': 'HTTP/1.1\r\n',
     'wsgi.errors': <cStringIO.StringO object at ...>,
     'wsgi.input': <cStringIO.StringI object at ...>,
     'wsgi.multiprocess': 0,
     'wsgi.multithread': 0,
     'wsgi.run_once': 0,
     'wsgi.url_scheme': 'http',
     'wsgi.version': (1, 0)}
    Marker: MARKER

Layers
------

Some basic layers useful for making test setups.

    >>> import os.path
    >>> from van.testing.layer import zcml_layer, null_layer

A zcml layer which sets up and tears down a zcml test harness (but is much
simpler than that provided with zope.app.functional):

    >>> class ZCMLLayer:
    ...     zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
    >>> zcml_layer(ZCMLLayer)

Some default layers are provided for use with zope.testing, a "null" layer that
specifically does nothing. This is useful for layers which inherit from other
layers but where you don't want setup/teardown functions run twice (is this a
zope.testing bug?):

    >>> class ExampleNullLayer(ZCMLLayer):
    ...     pass
    >>> null_layer(ExampleNullLayer)

This test runs in the layer van.testing.tests.ZCMLLayer, so we can get the
"test" utility but not the test_extra utility (see zcml_features.txt for an
example of a zcml layer with features):
        
    >>> from zope.interface import Interface
    >>> from zope.component import queryUtility
    >>> queryUtility(Interface, name="test", default='None')
    'MARKER'
    >>> queryUtility(Interface, name="test_extra", default='None')
    'None'
