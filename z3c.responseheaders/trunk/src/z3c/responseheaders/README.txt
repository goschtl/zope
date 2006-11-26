===================================
Response Header handling for Zope 3
===================================

This package provides an implementation for setting response headers
(e.g. for cache-control settings) on browser views by registering views
on views. This way we do not have to change view code in order to set
headers differently.

To demonstrate this behaviour we create a browserview and a content
class.

  >>> from zope.publisher.browser import BrowserView
  >>> from zope import component
  >>> from zope import interface

  >>> class IFoo(interface.Interface):
  ...     pass
  >>> class Foo(object):
  ...     interface.implements(IFoo)
  ...     pass
  >>> class IFooView(interface.Interface):
  ...     pass
  >>> class FooView(BrowserView):
  ...     interface.implements(IFooView)

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> foo = Foo()
  >>> view = FooView(foo, request)

Headers are applied by a handler on IBeforeTraverseEvent traversing
the view. We have to fire the event manually for testing.

  >>> from zope import event
  >>> from zope.app.publication.interfaces import BeforeTraverseEvent
  >>> event.notify(BeforeTraverseEvent(view, request))


In the normal case no cache headers are applied because no views
are registered.

  >>> request.response.getHeaders()
  [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)')]

Let us define a header setter view. The view has to provide to
IResponseHeaderSetter. There is a base class we can use.

  >>> from z3c.responseheaders import setter
  >>> class MySetter(setter.BaseSetter):
  ...     headers = (('My-Header','My Header Value'),)

And register the view.

  >>> from zope.app.testing import ztapi
  >>> from z3c.responseheaders.interfaces import IResponseHeaderSetter
  >>> ztapi.browserViewProviding(IFooView, MySetter, IResponseHeaderSetter)

And call the event handler again.

  >>> event.notify(BeforeTraverseEvent(view, request))
  >>> request.response.getHeaders()
  [('X-Powered-By', 'Zope (www.zope.org),
   Python (www.python.org)'),
   ('My-Header', 'My Header Value')]
