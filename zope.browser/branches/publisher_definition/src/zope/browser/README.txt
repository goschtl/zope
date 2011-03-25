IRequest
========

Requests are the fundamental entry point of a browser request.

There is not much we can test except that ``IRequest`` is importable
and an interface:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IRequest
  >>> Interface.providedBy(IRequest)
  True


IResponse
=========

Naturally, each request made to the server triggers a
response. Defined by IResponse, it mainly consist in a group of
headers and, optionnaly, a body.

There is not much we can test except that ``IResponse`` is importable
and an interface:

  >>> from zope.browser.interfaces import IResponse
  >>> Interface.providedBy(IResponse)
  True


IPublisher
==========

The publisher is the component responsable, usually, in transforming a
request into a response.

There is not much we can test except that ``IPublisher`` is importable
and an interface:

  >>> from zope.browser.interfaces import IPublisher
  >>> Interface.providedBy(IPublisher)
  True



IPublishingException
====================

A publishing exception is an exception raised during the publishing
process. The handling of such exception is therefore often handled
by the publisher component itself.

  >>> from zope.interface.common.interfaces import IException
  >>> from zope.browser.interfaces import IPublishingException
  >>> Interface.providedBy(IPublishingException)
  True
  >>> IPublishingException.extends(IException)
  True


IRedirect
---------

A redirect exception is a publishing exception that interrupt the
publishing in order to return a redirect-aware response.

  >>> from zope.browser.interfaces import IRedirect
  >>> Interface.providedBy(IRedirect)
  True
  >>> IRedirect.extends(IPublishingException)
  True


INotFound
---------

An exception meaning that the looked up object has not been found
during the publishing process.

  >>> from zope.browser.interfaces import INotFound
  >>> from zope.interface.common.interfaces import ILookupError
  >>> Interface.providedBy(INotFound)
  True
  >>> INotFound.extends(IPublishingException)
  True
  >>> INotFound.extends(ILookupError)
  True


IBadRequest
-----------

Bad request means the request is somehow malformed or erroneous.

  >>> from zope.browser.interfaces import IBadRequest
  >>> Interface.providedBy(IBadRequest)
  True
  >>> IBadRequest.extends(IPublishingException)
  True


IView
=====

Views adapt both a context and a request.

There is not much we can test except that ``IView`` is importable
and an interface:

  >>> from zope.interface import Interface
  >>> from zope.browser.interfaces import IView
  >>> Interface.providedBy(IView)
  True


IBrowserView
=============

Browser views are views specialized for requests from a browser (e.g.,
as distinct from WebDAV, FTP, XML-RPC, etc.).

There is not much we can test except that ``IBrowserView`` is importable
and an interface derived from ``IView``:

  >>> from zope.browser.interfaces import IBrowserView
  >>> Interface.providedBy(IBrowserView)
  True
  >>> IBrowserView.extends(IView)
  True


IDefaultViewName
================

A string that contains the default view name

  >>> from zope.browser.interfaces import IDefaultViewName
  >>> Interface.providedBy(IDefaultViewName)
  True


IAdding
=======

Adding views manage how newly=created items get added to containers.

There is not much we can test except that ``IAdding`` is importable
and an interface derived from ``IBrowserView``:

  >>> from zope.browser.interfaces import IAdding
  >>> Interface.providedBy(IBrowserView)
  True
  >>> IAdding.extends(IBrowserView)
  True


ITerms
======

The ``ITerms`` interface is used as a base for ``ISource`` widget
implementations.  This interfaces get used by ``zope.app.form`` and was
initially defined in ``zope.app.form.browser.interfaces``, which made it
impossible to use for other packages like ``z3c.form`` wihtout depending on
``zope.app.form``.

Moving such base components / interfaces to ``zope.browser`` makes it
possible to share them without undesirable dependencies.

There is not much we can test except that ITerms is importable
and an interface:

  >>> from zope.browser.interfaces import ITerms
  >>> Interface.providedBy(ITerms)
  True


ISystemErrorView
================

Views providing this interface can classify their contexts as system
errors. These errors can be handled in a special way (e. g. more
detailed logging).

There is not much we can test except that ISystemErrorView is importable
and an interface:

  >>> from zope.browser.interfaces import ISystemErrorView
  >>> Interface.providedBy(ISystemErrorView)
  True
