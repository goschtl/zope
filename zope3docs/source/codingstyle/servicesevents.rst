Services and Events

  A common pattern is where you have a persistent Service that uses
  subobjects as plugins.

  An example of this is the CachingService which contains Caches.
  The CachingService does not need to subscribe to events.
  The Caches need to subscribe to ObjectModifiedEvents.
  (They don't subscribe to moves or deletions, because the cache will
  time-out anyway before too long.)
  
  The Caches should not be subscribed directly to the EventService because
  the CachingService they are within may or may not be bound as a service.
  They should only be subscribed to the EventService when the CachingService
  is an active service.

  One way around this is to make the CachingService binding-aware, and also
  make the Caches binding-aware, and have the CachingService pass on such
  binding change notifications to the Caches.

  Another solution is to make the CachingService binding-aware, and also
  make it an EventChannel. There is a base-class that can be mixed into the
  CachingService implementation to make it a binding-aware EventChannel that
  subscribes to and unsubscribes from the EventService as required.

  In this case, a Cache can simply subscribe to its CachingService when it
  is added, and unsubscribe if it is removed.



<hr solid id=comments_below>


stevea (Nov 22, 2002 12:53 pm; Comment #1)  --
 A note from the pope: services such as this on generally shouldn't have subobjects that do work. The subobjects should be added to a persistent package, and the service should be configured to use them from there. This page will be refactored to take this into account soon.
 
