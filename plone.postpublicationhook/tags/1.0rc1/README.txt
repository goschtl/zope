Introduction
============

This package provides a hook into Zope's ZPublisher that is run after the
publisher has completed publication, but before the the transaction is commited
and the response is returned to the requesting browser. This is practical for
caching purposes: it is the ideal place to determine and insert caching headers
into the response.

Hooks use `zope.eventz_'s event mechanism using the
plone.validatehook.interfaces.IPostValidationEvent. This is based on the
standard ObjectEvent from `zope.component`_.

Example
=======

As an example we will write a bit of code which logs the path of every published
object. This is the code for the event handler::

    from zope.interface import Interface
    from zope.component import adapter
    from plone.postpublicationhook.interfaces import IAfterPublicationEvent
    import logging

    logger = logging.getLogger("LogRequest")

    @adapter(Interface, IAfterPublicationEvent)
    def LogRequest(object, event):
        if getattr(object, "getPhysicalPath", None) is None:
            path="Unknown path"
        else:
            path="/".join(object.getPhysicalPath()

        logger.info("Request for object %s" % path)


To use this code you need to register it in zcml::

    <subscriber handler=".events.LogRequest" />


.. _zope.event: http://pypi.python.org/pypi/zope.event
.. _zope.component: http://pypi.python.org/pypi/zope.component
