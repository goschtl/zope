Standard Events
===============

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.


IObjectEvent
------------

Import location: ``zope.component.interfaces.IObjectEvent``

The ``IObjectEvent`` is the base event triggered for all events on an
object.  The ``IObjectEvent`` is the base interface inheritted by for
all other events.  The object that generated this event is not
necessarily the object referred to by location.


IObjectCreatedEvent
-------------------

triggered when an object is created;

IObjectCopiedEvent
------------------

triggered when an object is copied;

IObjectModifiedEvent
--------------------

triggered when an object is modified;

IObjectAnnotationsModifiedEvent
-------------------------------

triggered when an object annotation is changed;

IObjectContentModifiedEvent
---------------------------

triggered when an object content is modified;

IRegistrationEvent
------------------

base interface, triggered fro register events;

IRegistrationActivatedEvent
---------------------------

triggered when a register is activated;

IRegistrationDeactivatedEvent
-----------------------------

triggered when a register is deactivated;

IObjectMovedEvent
-----------------

triggered when an object has move in a container;

IObjectAddedEvent
-----------------

triggered when an object has been added into a container;

IObjectRemovedEvent
-------------------

triggered when an object has been removed from a container;

IContainerModifiedEvent
-----------------------

triggered when a reordering, deletion or adding occurs in a container;

IBeforeTraverseEvent
--------------------

triggered when the publisher starts the traversal;

IEndRequestEvent
----------------

triggered when the publisher has finished the request calculation.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
