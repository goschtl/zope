z3c.bobopublisher
=================

This package provides a minimalistic reimplementation of the Zope publisher and
publication machinery using the bobo framework. It can be used as a simple
alternative for the following packages:

  * zope.app.publication
  * zope.app.publisher
  * zope.publisher
  * zope.traversing


The application
---------------

Let's create a sample application we can use to test bobopublisher:

    >>> from webtest import TestApp
    >>> from z3c.bobopublisher.application import Application
    >>> testapp = TestApp(Application())

Each request is mapped by bobo to a callable which will provide the response
for the client; if no specific bobo route matches the request's URL, the
bobopublisher Application object will try to traverse the URL components
starting from a root object.


The root object
---------------

The root object must be registered as an utility which provides the interface
zope.location.interfaces.IRoot:

    >>> testapp.get('/')
    Traceback (most recent call last):
    ...
    ComponentLookupError: (<InterfaceClass zope.location.interfaces.IRoot>, '')

We register a dummy root object with a single hard-coded sub-item for our
testing purposes:

    >>> from zope.component import adapts, getGlobalSiteManager
    >>> from zope.interface import implements, Interface
    >>> from zope.interface.common.mapping import IReadMapping
    >>> from zope.location.interfaces import IRoot
    >>> class Root(object):
    ...     implements(IRoot, IReadMapping)
    ...     def get(self, name, default=None):
    ...         return name == u'subitem' and SubItem() or default
    >>> class ISubItem(Interface):
    ...     pass
    >>> class SubItem(object):
    ...     implements(ISubItem)
    >>> getGlobalSiteManager().registerUtility(Root(), IRoot)


PublishTraverse adapters
------------------------

Now the application can find the root object, but we did not register any
PublishTraverse adapter, so every request will raise an exception:

    >>> testapp.get('/')
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', <Root object at ...>, <InterfaceClass z3c...>)

z3c.bobopublisher provides two generic PublishTraverse adapters:

    >>> from z3c.bobopublisher.traversing import PublishTraverse, PublishTraverseMapping
    >>> getGlobalSiteManager().registerAdapter(PublishTraverse)
    >>> getGlobalSiteManager().registerAdapter(PublishTraverseMapping)

It is now possible to perform a GET request on the test application:

    >>> testapp.get('/', status=404).body
    '...Not Found...'


Browser pages
-------------

Browser pages are named multi-adapters which adapt the context object and the
request; we register a browser page for the root object:

    >>> from z3c.bobopublisher.interfaces import IRequest
    >>> from zope.browser.interfaces import IBrowserView
    >>> class BrowserPage(object):
    ...     adapts(IRoot, IRequest)
    ...     implements(IBrowserView)
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...     def __call__(self):
    ...         return u'ABC'
    >>> getGlobalSiteManager().registerAdapter(BrowserPage, name='index.html')

Using the test application, we are able to call the page and get its result:

    >>> testapp.get('/index.html', status=200).body
    'ABC'

It is also possible to register a page for a specific HTTP method:

    >>> from z3c.bobopublisher.interfaces import IDELETERequest
    >>> class BrowserPageDelete(object):
    ...     adapts(IRoot, IDELETERequest)
    ...     implements(IBrowserView)
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...     def __call__(self):
    ...         return u'DELETE'
    >>> getGlobalSiteManager().registerAdapter(BrowserPageDelete, name='index.html')

Using the test application, we are able to call the page and get its result:

    >>> testapp.delete('/index.html', status=200).body
    'DELETE'


Traversing and locations
------------------------

After traversing an object, z3c.bobopublisher will locate the object setting
the parent and the name; if the traversed object doesn't provide the interface
ILocation it will be wrapped inside a location proxy.

If we traverse to the sub-item, we don't have any page defined:

    >>> testapp.get('/subitem/index.html', status=404).body
    '...Not Found...'

We register a browser page for the sub-item:

    >>> from z3c.bobopublisher.interfaces import IRequest
    >>> from zope.browser.interfaces import IBrowserView
    >>> class SubItemBrowserPage(object):
    ...     adapts(ISubItem, IRequest)
    ...     implements(IBrowserView)
    ...     def __init__(self, context, request):
    ...         self.context = context
    ...         self.request = request
    ...     def __call__(self):
    ...         return u'XYZ: %s' % repr(self.context.__parent__)
    >>> getGlobalSiteManager().registerAdapter(SubItemBrowserPage, name='index.html')

Using the test application, we are able to call the page and get its result:

    >>> testapp.get('/subitem/index.html', status=200).body
    'XYZ: <Root object at ...>'


Object proxies
--------------

z3c.bobopublisher is able to wrap published objects with a proxy; it provides a
filter middleware to configure the proxy factory:

    [filter-app:proxy]
    use = egg:z3c.bobopublisher#proxy
    proxy = zope.security.checker.ProxyFactory
    next = application

In this example, we configure a proxied application to use the ProxyFactory
from zope.security:

    >>> from z3c.bobopublisher.middleware import ProxyMiddleware
    >>> proxyapp = TestApp(ProxyMiddleware(Application(),
    ...     'zope.security.checker.ProxyFactory'))

Using the test application, we are able to call the page and get its result:

    >>> proxyapp.get('/subitem/index.html')
    Traceback (most recent call last):
    ....
    ForbiddenAttribute: ('get', <Root object at ...>)


Defining browser pages with ZCML
--------------------------------

z3c.bobopublisher provides ZCML directives that can be used to define browser
pages and the name of the default page.

    >>> from zope.configuration import config, xmlconfig
    >>> context = config.ConfigurationMachine()
    >>> xmlconfig.registerCommonDirectives(context)
    >>> context = xmlconfig.string("""<?xml version="1.0"?>
    ... <configure xmlns="http://namespaces.zope.org/bobo">
    ...   <include package="z3c.bobopublisher" file="meta.zcml" />
    ...   <page
    ...       name="something.html"
    ...       for="zope.location.interfaces.IRoot"
    ...       class="z3c.bobopublisher.tests.TestBrowserPage"
    ...       />
    ...   <page
    ...       name="delete.html"
    ...       for="zope.location.interfaces.IRoot"
    ...       class="z3c.bobopublisher.tests.TestBrowserPage"
    ...       methods="DELETE"
    ...       />
    ...   <defaultView
    ...       name="something.html"
    ...       for="zope.location.interfaces.IRoot"
    ...       />
    ... </configure>
    ... """, context=context, execute=True)

Using the test application, we are able to call the page and get its result:

    >>> testapp.get('/something.html', status=200).body
    'TEST PAGE'

As shown above, it is possible to register browser pages for one or more
specific HTTP methods:

    >>> testapp.delete('/delete.html', status=200).body
    'TEST PAGE'

    >>> testapp.get('/delete.html', status=404).body
    '...Not Found...'

We also registered 'something.html' as the default view name for the root
object:

    >>> testapp.get('/', status=200).body
    'TEST PAGE'


Resources
---------

z3c.bobopublisher provides a ZCML directive which can be used to publish static
resources from a directory in the filesystem:

    >>> import os, tempfile
    >>> tempdir = tempfile.mktemp()
    >>> os.mkdir(tempdir)
    >>> open(os.path.join(tempdir, 'resource.txt'), 'w').write('RESOURCE')

    >>> context = xmlconfig.string("""<?xml version="1.0"?>
    ... <configure xmlns="http://namespaces.zope.org/bobo">
    ...   <resources
    ...       name="images"
    ...       directory="%s"
    ...       />
    ... </configure>
    ... """ % tempdir, context=context, execute=True)

By the default resources are registered for the IRoot interface, as shown below:

    >>> testapp.get('/images', status=302).body
    'See http://localhost/images/'

    >>> testapp.get('/images/', status=200).body
    '...resource.txt...'

    >>> response = testapp.get('/images/resource.txt', status=200)
    >>> response.content_type, response.charset, response.body
    ('text/plain', 'UTF-8', 'RESOURCE')

    >>> response.headers['Cache-Control']
    'public,max-age=86400'
    >>> 'Expires' in response.headers
    True
    >>> 'Last-Modified' in response.headers
    True

It is not possible to quit from the path of the resource directory:

    >>> testapp.get('/images/../images/resource.txt', status=404).body
    '...Not Found...'

We can remove now the temporary directory:

    >>> os.unlink(os.path.join(tempdir, 'resource.txt'))
    >>> os.rmdir(tempdir)
