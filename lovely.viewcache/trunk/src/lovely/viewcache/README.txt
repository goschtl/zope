==========
View Cache
==========


Test Setup
----------

Because the view cache uses a utility to store the cached value we provide a
cache utility here.

  >>> from zope import component
  >>> from lovely.viewcache.ram import ViewCache
  >>> from lovely.viewcache.interfaces import IViewCache
  >>> cache = ViewCache()
  >>> component.provideUtility(cache, IViewCache)

We need some content to use as context.

  >>> from zope.app.container.contained import Contained
  >>> from zope import interface
  >>> class IContent(interface.Interface):
  ...     pass
  >>> class Content(Contained):
  ...     interface.implements(IContent)
  ...     def __init__(self, name):
  ...         self.count = 0
  ...         self.name = name
  >>> content = Content(u'content 1')
  >>> root[u'content'] = content

A browser is also needed.

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest() 

Then we need a view which we try to cache. The view we define here is a normal
implementation of a view. The view renders a result which depends on a counter
in it's context. The counter is incremented every time the view is rendered.
This allows us to check if the result is coming from the cache.

  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> from zope.publisher.browser import BrowserView
  >>> class View(BrowserView):
  ...     def __call__(self, *args, **kwargs):
  ...         self.context.count += 1
  ...         return u'"%s" is rendered %s time(s)'% (
  ...                           self.context.name, self.context.count)


Cached View
-----------

For the caching of views we provide a special adapter factory for views.

  >>> from lovely.viewcache.view import cachedView

To make the view cached we create a cached view class from the original view
class.

  >>> CachedView = cachedView(View, dependencies = ('content',))

Instead of registering the original view class we can now use the newly
created view class.

  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> component.provideAdapter(CachedView,
  ...                          (IContent, IDefaultBrowserLayer),
  ...                          IBrowserView,
  ...                          name='cachedView')

If we now lookup our view we get an instance of the view which is proxied by
the cache manager view.

  >>> view = component.getMultiAdapter((content, request), name='cachedView')
  >>> view.__name__ = 'cachedView'
  >>> from lovely.viewcache.view import CachedViewMixin
  >>> isinstance(view, CachedViewMixin)
  True

When we render the view by calling it we get the result.

  >>> view()
  u'"content 1" is rendered 1 time(s)'

Rendering the view again will return the same result because the cached result
is used.

  >>> view()
  u'"content 1" is rendered 1 time(s)'

The cachingOn property allows the control of the caching of the view. If
cachingOn returns False the view is not cached.

  >>> view.cachingOn
  True
  >>> view.cachingOn = False
  >>> view()
  u'"content 1" is rendered 2 time(s)'

If we switch back we get the old cached value back.

  >>> view.cachingOn = True
  >>> view()
  u'"content 1" is rendered 1 time(s)'

We invalidate the cache entry.

  >>> cache = component.queryUtility(IViewCache)
  >>> cache.invalidate(dependencies=['content'])

And the view will be rendered and cached again.

  >>> view()
  u'"content 1" is rendered 3 time(s)'
  >>> view()
  u'"content 1" is rendered 3 time(s)'

If we request a new view we get the already cached value.

  >>> view = component.getMultiAdapter((content, request), name='cachedView')
  >>> view.__name__ = 'cachedView'
  >>> view()
  u'"content 1" is rendered 3 time(s)'


Views On Different Contexts
---------------------------

If the view is used in another context it creates a new cache entry.

  >>> content2 = Content(u'content 2')
  >>> root[u'content2'] = content2

  >>> view2 = component.getMultiAdapter((content2, request), name='cachedView')
  >>> view2()
  u'"content 2" is rendered 1 time(s)'
  >>> view2()
  u'"content 2" is rendered 1 time(s)'


Providing static dependencies
-----------------------------

A cached view provides the static dependencies via the 'staticCachingDeps'
attribute. The static dependency can be set as a class member or can be
provided when creating the cached view. It can not be cached during runtime.

  >>> view.staticCachingDeps
  ('content',)
  >>> view.staticCachingDeps = ('not possible',)
  Traceback (most recent call last):
  ...
  AttributeError: can't set attribute


Providing dynamic dependencies
------------------------------

The view can provide dynamic dependencies via the 'dynamicCachingDeps'
attribute.

  >>> view.dynamicCachingDeps
  ()
  >>> view.dynamicCachingDeps = ('changeable',)
  >>> view.dynamicCachingDeps
  ('changeable',)


Using 'minAge'
--------------

A view with a different name get's a different cache entry. It is also
possible to provide a minAge for the cache entry.

  >>> AnotherCachedView = cachedView(View,
  ...                                dependencies = ('content',),
  ...                                minAge=1)
  >>> component.provideAdapter(AnotherCachedView,
  ...                          (IContent, IDefaultBrowserLayer),
  ...                          IBrowserView,
  ...                          name='anotherCachedView')
  >>> view = component.getMultiAdapter((content, request), name='anotherCachedView')
  >>> view.__name__ = 'anotherCachedView'
  >>> view()
  u'"content 1" is rendered 4 time(s)'

Because of the minimum age if we invalidate the the cache the new view is not
removed from the cache.

  >>> cache.invalidate(dependencies=['content'])
  >>> view()
  u'"content 1" is rendered 4 time(s)'


Cached Viewlets
---------------

Caching for viewlets can be used the same as cached views are used.

  >>> from lovely.viewcache.view import cachedViewlet

  >>> from zope.viewlet.viewlet import ViewletBase
  >>> class Viewlet(ViewletBase):
  ...     def update(self):
  ...         self.context.count += 1
  ...     def render(self):
  ...         return u'viewlet for context "%s" is rendered %s time(s)'% (
  ...                           self.context.name, self.context.count)

  >>> CachedViewlet = cachedViewlet(Viewlet, dependencies=('viewlet',))

Now we can build a viewlet instance from the cached viewlet.

  >>> content3 = Content(u'content 3')
  >>> root[u'content3'] = content3
  >>> viewlet = CachedViewlet(content3, request, None, None)
  >>> from lovely.viewcache.view import CachedViewletMixin
  >>> isinstance(viewlet, CachedViewletMixin)
  True

  >>> viewlet.update()
  >>> viewlet.render()
  u'viewlet for context "content 3" is rendered 1 time(s)'

Because the viewlet is now cached update is not called again. Because the
update method increments the count in the context we check for a change on the
count.

  >>> content3.count
  1
  >>> viewlet.update()
  >>> content3.count
  1

Also rendering the viewlet again will return the cached value.

  >>> viewlet.render()
  u'viewlet for context "content 3" is rendered 1 time(s)'

  >>> cache.invalidate(dependencies=['viewlet'])
  >>> viewlet.update()
  >>> viewlet.render()
  u'viewlet for context "content 3" is rendered 2 time(s)'


Subclassing Cached Views
------------------------

Subclassing a cached view is possible but if __call__ is used in a derived
class caching is only done for the values from the base class.

  >>> class DerivedView(CachedView):
  ...     def __call__(self):
  ...         return u'Derived was called'
  >>> cachedDerivedView = cachedView(DerivedView)
  >>> derived = cachedDerivedView(content, request)
  >>> derived.__name__ = 'derived'
  >>> derived()
  u'Derived was called'
  >>> derived()
  u'Derived was called'

