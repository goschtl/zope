Overview
========

This package integrates `zope.globalrequest <http://pypi.python.org/pypi/zope.globalrequest>`_
with Zope 2. It is compatible with Zope 2.12 and later. In Zope 2.10, you
can install `ZPublisherEventsBackport <http://pypi.python.org/pypi/ZPublisherEventsBackport>`_
to use it.

The only thing you need to do to use this package is to load its configuration
from your own ZCML file::

    <include package="five.globalrequest" />

You can now use ``zope.globalrequest`` as normal::

    from zope.globalrequest import getRequest
    request = getRequest()

The request is set up when publication starts, when the ``IPubStart`` event
is fired. It is cleared on one of the ``IPubEnd`` events: ``IPubSuccess`` or
``IPubFailure``. If you have your own event handlers for either of these
events, you should be aware that the event setup/clear could happen after/
before your own event handler is executed, since the order of execution for
event handlers is not controllable.
