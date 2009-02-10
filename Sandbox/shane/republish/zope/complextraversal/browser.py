

from zope.location import Location

from zope.complextraversal.interfaces import IBrowserView
from zope.complextraversal.interfaces import IBrowserPage


class BrowserView(Location):
    """Browser View.

    >>> view = BrowserView("context", "request")
    >>> view.context
    'context'
    >>> view.request
    'request'

    >>> view.__parent__
    'context'
    >>> view.__parent__ = "parent"
    >>> view.__parent__
    'parent'
    """
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __getParent(self):
        return getattr(self, '_parent', self.context)

    def __setParent(self, parent):
        self._parent = parent

    __parent__ = property(__getParent, __setParent)


class BrowserPage(BrowserView):
    """Browser page

    To create a page, which is an object that is published as a page,
    you need to provide an object that:

    - has a __call__ method and that

    - provides IBrowserPublisher, and

    - if ZPT is going to be used, then your object should also provide
      request and context attributes.

    The BrowserPage base class provides a standard constructor and a
    simple implementation of IBrowserPublisher:

      >>> class MyPage(BrowserPage):
      ...     pass

      >>> request = TestRequest()
      >>> context = object()
      >>> page = MyPage(context, request)

      >>> from zope.publisher.interfaces.browser import IBrowserPublisher
      >>> IBrowserPublisher.providedBy(page)
      True

      >>> page.browserDefault(request) == (page, ())
      True

      >>> page.publishTraverse(request, 'bob') # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      NotFound: Object: <zope.publisher.browser.MyPage object at ...>, name: 'bob'

      >>> page.request is request
      True

      >>> page.context is context
      True

    But it doesn't supply a __call__ method:

      >>> page()
      Traceback (most recent call last):
        ...
      NotImplementedError: Subclasses should override __call__ to provide a response body

    It is the subclass' responsibility to do that.

    """
    implements(IBrowserPage)

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        raise NotFound(self, name, request)

    def __call__(self, *args, **kw):
        raise NotImplementedError("Subclasses should override __call__ to "
                                  "provide a response body")
