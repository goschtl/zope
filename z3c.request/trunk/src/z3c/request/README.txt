z3c.request
===========

This package provides a common interface for browser request implementations.

There is not much we can test except that IRequest is importable and an
interface:

    >>> from z3c.request.interfaces import IRequest
    >>> from zope.interface import Interface
    >>> Interface.providedBy(IRequest)
    True

The WebOb Request class will automatically implement the IRequest interface:

    >>> import webob
    >>> IRequest.implementedBy(webob.Request)
    True

WebOb Request objects will automatically provide the IRequest interface:

    >>> obj = webob.Request.blank('/test')
    >>> IRequest.providedBy(obj)
    True

The zope.publisher Request classes will automatically implement the IRequest
interface:

    >>> from zope.publisher.base import BaseRequest
    >>> IRequest.implementedBy(BaseRequest)
    True

The zope.publisher Request objects will automatically provide the IRequest
interface:

    >>> request = BaseRequest(None, None)
    >>> IRequest.providedBy(request)
    True

