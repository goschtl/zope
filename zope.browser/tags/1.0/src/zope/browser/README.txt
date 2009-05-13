IView
-----

Views adapt both a context and a request.

There is not much we can test except that ``IView`` is importable
and an interface:

.. doctest::

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IView
  >>> Interface.providedBy(IView)
  True

IBrowserView
-------------

Browser views are views specialized for requests from a browser (e.g.,
as distinct from WebDAV, FTP, XML-RPC, etc.).

There is not much we can test except that ``IBrowserView`` is importable
and an interface derived from ``IView``:

.. doctest::

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IBrowserView
  >>> Interface.providedBy(IBrowserView)
  True
  >>> IBrowserView.extends(IView)
  True

ITerms
------

The ``ITerms`` interface is used as a base for ``ISource`` widget
implementations.  This interfaces get used by ``zope.app.form`` and was
initially defined in ``zope.app.form.browser.interfaces``, which made it
impossible to use for other packages like ``z3c.form`` wihtout depending on
``zope.app.form``.

Moving such base components / interfaces to ``zope.browser`` makes it
possible to share them without undesirable dependencies.

There is not much we can test except that ITerms is importable
and an interface:

.. doctest::

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import ITerms
  >>> Interface.providedBy(ITerms)
  True
