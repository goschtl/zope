========
z3c.noop
========

z3c.noop provides traverser that simply skips a path element,
so /foo/++noop++qux/bar is equivalent to /foo/bar.

This is useful for example to generate varying URLs to work around browser
caches[#test-setup]_.

>>> dummy = object()
>>> root['foo'] = dummy
>>> traverse('/foo') == dummy
True
>>> traverse('/++noop++12345/foo') == dummy
True



.. [#test-setup]

    >>> import zope.traversing.api
    >>> import zope.publisher.browser

    >>> root = getRootFolder()
    >>> request = zope.publisher.browser.TestRequest()

    >>> def traverse(path):
    ...     return zope.traversing.api.traverse(root, path, request=request)
