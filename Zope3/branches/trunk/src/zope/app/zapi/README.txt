Zope Application Programming Interface
======================================

This package provides a collection of commonly used APIs to make
imports simpler.

Mostly, the APIs provided here are imported from elsewhere. A few are
provided here.

principals()
------------

The principals method returns the authentication service. If no
service is defined, a ComponentLookupError is raised:

  >>> from zope.app import zapi
  >>> zapi.principals() #doctest: +NORMALIZE_WHITESPACE
  Traceback (most recent call last):
  ...
  ComponentLookupError:
  (<InterfaceClass zope.app.security.interfaces.IAuthenticationUtility>, '')


But if we provide an authentication service:

  >>> import zope.interface
  >>> from zope.app.security.interfaces import IAuthenticationUtility
  >>> class FakeAuthenticationUtility:
  ...     zope.interface.implements(IAuthenticationUtility)
  >>> fake = FakeAuthenticationUtility()
  
  >>> from zope.app.tests import ztapi
  >>> ztapi.provideUtility(IAuthenticationUtility, fake)

Then we should be able to get the service back when we ask for the
principals: 

  >>> zapi.principals() is fake
  True

    

