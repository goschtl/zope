=================
Respsonse Caching
=================

This package allows to cache results of ContentProviders. Note that
normal zope BrowserViews do not implement the IContentProvider
interface, so in order to cache views, they have to implement the
update and render methods. For a base class see
z3c.viewtemplate.baseview.BaseView.

IResponseCacheSettings Views
============================

In oder to be cached, a view implementing IResponseCacheSettings has
to be registered for the provider and the beforupdate handler also.

    >>> from zope import component
    >>> from lovely.responsecache.event import setCache
    >>> component.provideHandler(setCache)

There is a base class which can be used to create cache settings views.

    >>> from lovely.responsecache import view

Let us define a dedicated memcached client for our responsecache.

    >>> from lovely.memcached.utility import MemcachedClient
    >>> from lovely.memcached.interfaces import IMemcachedClient
    >>> util = MemcachedClient()
    >>> util.invalidateAll()
    >>> component.provideUtility(util, IMemcachedClient,
    ...     name='responsecache')
    
Make sure the local memcached client is running:

    >>> util.getStatistics() != []
    True

Let us create a simple view and settings view. We have to have a view
that implements IContentProvider.

    >>> from zope.publisher.browser import BrowserView
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope import interface
    >>> from zope.contentprovider.interfaces import IContentProvider
    >>> from zope.contentprovider.interfaces import BeforeUpdateEvent
    >>> from zope.event import notify
    >>> class MyView(BrowserView):
    ...     interface.implements(IContentProvider)
    ...     __name__ = u'test.html'
    ...     __parent__ = root
    ...     def update(self):
    ...         pass
    ...     def render(self):
    ...         return 'my view content'
    ...     def __call__(self):
    ...         notify(BeforeUpdateEvent(self, self.request))
    ...         self.update()
    ...         return self.render()

If we call the view without having cache settings nothing is
cached. We can evaluate this by looking at the responseheaders.

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> myView = MyView(root, request)
    >>> myView()
    'my view content'
    >>> request.response.getHeaders()
    [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)')]

Let us now implement cache setttings.

    >>> class MyDefaultCacheSettings(view.ResponseCacheSettings):
    ...     component.adapts(IContentProvider, IBrowserRequest)
    ...     lifetime=3600
    ...     cacheName = 'responsecache'
    >>> component.provideAdapter(MyDefaultCacheSettings)
    >>> myView()
    'my view content'

We now have a cache miss.

    >>> request.response.getHeaders()
    [...('X-Memcached-Miss', '/test.html')]

Note that the render method gets rewritten.

    >>> myView.render
    <lovely.responsecache.event.RenderWrapper object at ...>

But if we now try again we have a hit.

    >>> request = TestRequest(PATH_INFO='test.html')
    >>> myView = MyView(object(), request)
    >>> myView()
    u'my view content'
    >>> request.response.getHeaders()
    [...('X-Memcached-Hit', '/test.html')]


Note that the render and update methods are rewritten.

    >>> myView.render
    <lovely.responsecache.event.RenderWrapper object at ...>
    >>> myView.update
    <lovely.responsecache.event.UpdateWrapper object at ...>
    
