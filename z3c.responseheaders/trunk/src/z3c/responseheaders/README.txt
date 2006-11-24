===================================
Response Header handling for Zope 3
===================================

This package provides an implementation for setting response headers
(e.g. for chahe settings) on browser views by providing adapters to
views. This way we do not have to change view code in order to set
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
  ...     def __call__(self):
  ...         return u'i am so foo'

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> foo = Foo()
  >>> view = FooView(foo, request)

Headers are applied before traversing the view. We do not set up
events for this test because we don't need it. We just call the
handler directly

  >>> from z3c.responseheaders import setter
  >>> setter.onBrowserViewBeforeTraverse(view, request)

In the normal case no cache headers are applied because no adapters
are registered.

  >>> request.response.getHeaders()
  [('X-Powered-By', 'Zope (www.zope.org), Python (www.python.org)')]

Let us define a header setter adapter. The adapter has to adapt
(context, view) to IResponseHeaderSetter.

  >>> class MySetter(setter.BaseSetter):
  ...     component.adapts(IFooView)
  ...     headers = (('My-Header','My Header Value'),)

  >>> component.provideAdapter(MySetter)

And call the event handler again.

  >>> setter.onBrowserViewBeforeTraverse(view, request)
  >>> request.response.getHeaders()
  [('X-Powered-By', 'Zope (www.zope.org),
   Python (www.python.org)'),
   ('My-Header', 'My Header Value')]
