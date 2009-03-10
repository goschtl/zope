=========
Ownership
=========

This package provides simple ownership support for objects that has an
IPrincipalRoleManager adapter, and that means almost any persistent object
when using zope.securitypolicy.


IOwnership interface
--------------------

First, let's create example content class. Note, that it must implement
IOwnerAware class, and for zope.securitypolicy adapters, it also must implement
IAnnotatable.

  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from zope.interface import implements, Interface
  >>> from z3c.ownership.interfaces import IOwnerAware
  
  >>> class IContent(Interface):
  ...     pass
  
  >>> class Content(object):
  ...
  ...     implements(IContent, IAttributeAnnotatable, IOwnerAware)
  
  >>> content = Content()

The object can now be adapted to IOwnership interface that provides the "owner"
attribute.

  >>> from z3c.ownership.interfaces import IOwnership
  >>> ownership = IOwnership(content)

Default owner is unset, so it's None

  >>> ownership.owner is None
  True

It uses the IAuthentication utility for looking up principals. For this test,
we have simple principalRegistry registered as an utility. Let's use it to
define two principals

  >>> dan = authentication.definePrincipal('dan', 'Dan', login='dan')
  >>> bob = authentication.definePrincipal('bob', 'Bob', login='bob')

Now, let's make dan an owner of our content object

  >>> ownership.owner = dan

Let's check it out
  
  >>> ownership = IOwnership(content)
  >>> ownership.owner is dan
  True

When principal owns an object, it has the ``z3c.ownership.Owner`` role on that
object. The name of the role is also available as `OWNER_ROLE` constant from
``z3c.ownership.interfaces``.

  >>> from z3c.ownership.interfaces import OWNER_ROLE
  >>> OWNER_ROLE == 'z3c.ownership.Owner'
  True

Let's check if dan has a "z3c.ownership.Owner" role for this object

  >>> from zope.securitypolicy.interfaces import IPrincipalRoleMap
  >>> rolemap = IPrincipalRoleMap(content)

  >>> rolemap.getPrincipalsAndRoles()
  [('z3c.ownership.Owner', 'dan', PermissionSetting: Allow)]

Now, let's change the owner. Note, that when changing an owner, the
OwnerChangedEvent is fired, let's check it out.

  >>> def printEvent(object, event):
  ...     old = (event.oldOwner is not None) and event.oldOwner.id or None
  ...     new = (event.newOwner is not None) and event.newOwner.id or None
  ...     print old, '->', new

  >>> from z3c.ownership.interfaces import IOwnerChangedEvent
  >>> from zope.component import provideHandler
  >>> provideHandler(printEvent, adapts=(IContent, IOwnerChangedEvent))

First, let's check changing owners to None (to remove ownership at all)

  >>> ownership.owner = None
  dan -> None

  >>> rolemap.getPrincipalsAndRoles()
  []

Let's set owner to bob

  >>> ownership.owner = bob
  None -> bob

  >>> rolemap.getPrincipalsAndRoles()
  [('z3c.ownership.Owner', 'bob', PermissionSetting: Allow)]

Now, let's change owner back to dan.

  >>> ownership.owner = dan
  bob -> dan

  >>> rolemap.getPrincipalsAndRoles()
  [('z3c.ownership.Owner', 'dan', PermissionSetting: Allow)]

Note, that we can't use non IPrincipal object as an owner.

  >>> ownership.owner = object
  Traceback (most recent call last):
  ...
  ValueError: IPrincipal object or None required

If we'll try to set owner to same principal as it were, no event will be fired.

  >>> ownership.owner = dan

(note, that "dan -> dan" wasn't printed on this assignment)


Breaking ownership
------------------

There is possibility to break the system, if we assign z3c.ownership.Owner role
by hand, because object can only have one owner, so don't do it at all :)

  >>> rolemap.assignRoleToPrincipal('z3c.ownership.Owner', bob.id)

It will fail on getting the owner

  >>> ownership.owner
  Traceback (most recent call last):
  ...
  RuntimeError: Object has multiple owners. This should not happen
  
And on setting

  >>> ownership.owner = dan
  Traceback (most recent call last):
  ...
  RuntimeError: Object has multiple owners. This should not happen

If we remove all z3c.ownership.Owner roles by hand, the owner will be None

  >>> rolemap.unsetRoleForPrincipal('z3c.ownership.Owner', dan.id)
  >>> rolemap.unsetRoleForPrincipal('z3c.ownership.Owner', bob.id)
  >>> ownership.owner is None
  True


Ownership subscriber
--------------------

This package also provides a subscriber for IObjectAddedEvent that sets
current interaction principal as object owner

Let's create new interaction and participation

  >>> from zope.security.management import endInteraction, newInteraction

  >>> class Participation(object):
  ...     interaction = None

  >>> participation = Participation()
  >>> participation.principal = bob

  >>> endInteraction()
  >>> newInteraction(participation)

Now, let's create object and notify system with ObjectCreatedEvent

  >>> from zope.event import notify
  >>> from zope.lifecycleevent import ObjectCreatedEvent
  
  >>> content2 = Content()
  >>> notify(ObjectCreatedEvent(content2))
  None -> bob

Note that we also catched the OwnerChangedEvent with the handler we
registered above.

Let's check if our object has an owner

  >>> IOwnership(content2).owner is bob
  True

If there's no participation active or principal can't be get for some reason,
owner won't be set.

  >>> endInteraction()
  >>> content3 = Content()
  >>> notify(ObjectCreatedEvent(content3))
  >>> IOwnership(content3).owner is None
  True


Unexistant principals
---------------------

If principal that owns the object doesn't exist anymore, the ``owner`` attribute
will be None.

  >>> content4 = Content()
  >>> IOwnership(content4).owner = dan
  None -> dan

  >>> authentication._clear()
  >>> IOwnership(content4).owner is None
  True
