Instance-based Event Subscription Support
=========================================

This package implements support for subscribing to events for a
particular instance of an object.  This package implements the proposal
found at http://dev.zope.org/Zope3/InstanceAndTypeBasedSubscriptions .

The package provides an event channel for dispatching events to the
appropriate instance as well as an adapter from `IAnnotatable` to
`IObservable`.  This is important because an object must support
`IAnnotatable` (and therefore `IAnnotations`) in order to support
instance-based subscriptions.

Subscriptions for a particular instance are stored in the instance's
annotations, in a key defined in `zope.app.observable.observable.key`
(currently 'zope.app.observable').  The annotation stored in the key
is actually an Observers object, which is a local registry that is not
aware of the global registry in any way.  More information on the
Observers object is available in observers.txt.
