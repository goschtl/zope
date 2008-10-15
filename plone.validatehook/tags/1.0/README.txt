Introduction
============

This package provides a hook into Zope's ZPublisher that is run after
the publisher has completed traversal and authentication, but before
it tries to publish an object. This is practical for tasks such as
tracking user activity.

Hooks use `zope.event`_'s event mechanism using the
plone.validatehook.interfaces.IPostValidationEvent. This is based on
the standard ObjectEvent form `zope.component`_. 

The IPostValidationEvent event has two attributes: ``user`` which is the
currently authenticated user object and ``request``, which is the current
request object. 

  *Keep in mind that even unauthenticated requests have a user
  object. If you only want to deal with 'normal' users make sure
  you ignore any instances of AccessControl.User.SpecialUser.*


Example
=======

As an example we will write a bit of code which logs the id of the
current user and the path to the current code. This is the code for
the event handler::

    from zope.interface import Interface
    from zope.component import adapter
    from plone.validatehook.interfaces import IPostValidationEvent
    import logging

    logger = logging.getLogger("LogRequest")

    @adapter(Interface, IPostValidationEvent)
    def LogRequest(object, event):
        if getattr(object, "getPhysicalPath", None) is None:
            path="Unknown path"
        else:
            path="/".join(object.getPhysicalPath()

        logger.info("Request from user '%s' for object %s" %
                event.user.getId(), path)

To use this code you need to register it in zcml::

    <subscriber handler=".events.LogRequest" />


.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.event: http://pypi.python.org/pypi/zope.event

