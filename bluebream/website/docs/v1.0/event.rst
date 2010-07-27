.. _std-events:

Standard Events
===============

IObjectEvent
------------

Import location: ``zope.component.interfaces.IObjectEvent``

The ``IObjectEvent`` is the base event triggered for all events on an
object.  The ``IObjectEvent`` is the base interface inherited by for
all other events.  The object that generated this event is not
necessarily the object referred to by location.


IObjectCreatedEvent
-------------------

Import location: ``zope.lifecycleevent.interfaces.IObjectCreatedEvent``

This event is triggered when an object is created.

IObjectCopiedEvent
------------------

Import location: ``zope.lifecycleevent.interfaces.IObjectCopiedEvent``

This event is triggered when an object is copied.

IObjectModifiedEvent
--------------------

Import location: ``zope.lifecycleevent.interfaces.IObjectModifiedEvent``

This event is triggered when an object is modified.

IObjectAnnotationsModifiedEvent
-------------------------------

This event is triggered when an object annotation is changed.

IObjectContentModifiedEvent
---------------------------

This event is triggered when an object content is modified.

IRegistrationEvent
------------------

Import location: ``zope.component.interfaces.IRegistrationEvent``

This is base interface for all registration related events.  This
event is triggered for register events.

IRegistered
-----------

Import location: ``zope.component.interfaces.IRegistered``

This event is triggered when a component or factory was registered.

IUnregistered
-------------

Import location: ``zope.component.interfaces.IUnregistered``

This event is triggered when a component or factory was unregistered.

IObjectMovedEvent
-----------------

Import location: ``zope.lifecycleevent.interfaces.IObjectMovedEvent``

This event is triggered when an object has move in a container.

IObjectAddedEvent
-----------------

Import location: ``zope.lifecycleevent.interfaces.IObjectAddedEvent``

This event is triggered when an object has been added into a
container.

IObjectRemovedEvent
-------------------

Import location: ``zope.lifecycleevent.interfaces.IObjectRemovedEvent``

This event is triggered when an object has been removed from a
container.

IContainerModifiedEvent
-----------------------

Import location: ``zope.container.interfaces.IContainerModifiedEvent``

This event is triggered when a reordering, deletion or adding occurs
in a container.

IBeforeTraverseEvent
--------------------

Import location: ``zope.traversing.interfaces.IBeforeTraverseEvent``

This event is triggered when the publisher starts the traversal.

IEndRequestEvent
----------------

Import location: ``zope.publisher.interfaces.IEndRequestEvent``

This event is triggered when the publisher has finished the request
calculation.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
