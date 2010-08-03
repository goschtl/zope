========
z3c.noop
========

z3c.noop provides traverser that simply skips a path element,
so /foo/++noop++qux/bar is equivalent to /foo/bar.

This is useful for example to generate varying URLs to work around
browser caches.


Set up
======

To show the behavior of the noop traverser we need a trversable dummy
object and a request:


>>> root = getRootFolder()
>>> dummy = object()
>>> root['foo'] = dummy

>>> import zope.publisher.browser
>>> request = zope.publisher.browser.TestRequest()

Noop traverser
==============

When the noop traverser is in the URL it does nothing. Traversal leads
to the same object:

>>> import zope.traversing.api
>>> zope.traversing.api.traverse(root, '/foo', request=request) == dummy
True
>>> zope.traversing.api.traverse(root, '/++noop++12345/foo',
...     request=request) == dummy
True
