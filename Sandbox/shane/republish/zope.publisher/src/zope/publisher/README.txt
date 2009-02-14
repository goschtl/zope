
BrowserView Tests
-----------------

    >>> from zope.publisher.browser import BrowserView
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

BrowserPage Tests
-----------------

To create a page, which is an object that is published as a page,
you need to provide an object that:

- has a __call__ method and that

- provides IBrowserPublisher, and

- if ZPT is going to be used, then your object should also provide
    request and context attributes.

The BrowserPage base class provides a standard constructor and a
simple implementation of IBrowserPage:

    >>> from zope.publisher.browser import BrowserPage
    >>> class MyPage(BrowserPage):
    ...     pass

    >>> request = object()
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
    NotFound: Object: <MyPage object at ...>, name: 'bob'

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
