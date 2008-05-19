=================
Content ownership
=================

This package implement single ownership concept. Content owner has special
role on content `content.Owner`.

We need setup security interaction and principals

  >>> from zope import interface, component, event
  >>> import zope.security.management
  >>> from z3ext.ownership import tests
  >>> from z3ext.ownership.interfaces import IOwnership
  >>> from z3ext.ownership.interfaces import IOwnerAware, IOwnerGroupAware

  >>> from zope.app.security.interfaces import IAuthentication
 
  >>> principal1 = tests.Principal('bob')
  >>> principal2 = tests.Principal('meg')

  >>> class Auth(object):
  ...    interface.implements(IAuthentication)
  ...
  ...    def getPrincipal(self, id):
  ...       if id == 'bob':
  ...          return principal1
  ...       if id == 'meg':
  ...          return principal2

  >>> auth = Auth()
  >>> component.provideUtility(auth)

  >>> participation = tests.Participation()
  >>> participation.principal = principal1
  >>> zope.security.management.endInteraction()
  >>> zope.security.management.newInteraction(participation)
  >>> interaction = zope.security.management.getInteraction()

  >>> from zope.lifecycleevent import ObjectCreatedEvent
  >>> from zope.annotation.interfaces import IAttributeAnnotatable

  >>> class IMyObject(IOwnerAware):
  ...   pass

  >>> class Content:
  ...    __parent__ = None
  ...    interface.implements(IAttributeAnnotatable, IMyObject)

  >>> content = Content()
  >>> event.notify(ObjectCreatedEvent(content))

  >>> owner = IOwnership(content)

  >>> owner.owner
  <Principal 'bob'>

  >>> owner.ownerId
  'bob'

Now let's check owner roles

  >>> from z3ext.security.interfaces import IExtendedGrantInfo

  >>> grantinfo = IExtendedGrantInfo(content)
  >>> grantinfo.getPrincipalsForRole('content.Owner')
  [('bob', PermissionSetting: Allow)]

  >>> grantinfo.getRolesForPrincipal('bob')
  [('content.Owner', PermissionSetting: Allow)]

  >>> grantinfo.getRolesForPrincipal('meg')
  [('content.Owner', PermissionSetting: Deny)]

We can change owner

  >>> owner.owner = principal2

  >>> owner = IOwnership(content)

  >>> owner.owner
  <Principal 'meg'>

  >>> owner.ownerId
  'meg'

Change ownerId

  >>> owner.ownerId = 'bob'

  >>> owner = IOwnership(content)
  >>> owner.owner
  <Principal 'bob'>

  >>> owner.owner = principal2

  >>> grantinfo = IExtendedGrantInfo(content)
  >>> grantinfo.getRolesForPrincipal('meg')
  [('content.Owner', PermissionSetting: Allow)]

  >>> grantinfo.getRolesForPrincipal('bob')
  [('content.Owner', PermissionSetting: Deny)]

  >>> grantinfo.getPrincipalsForRole('unknown.Role')
  []

content.Owner and content.GroupOwner are disabled for principal bob 
so ownership is not inherited from parents. But we can change this, we should 
explicitly set marker interface for content

  >>> from z3ext.ownership.interfaces import IInheritOwnership
  >>> interface.directlyProvides(content, IInheritOwnership)

  >>> grantinfo = IExtendedGrantInfo(content)
  >>> grantinfo.getRolesForPrincipal('bob')
  []


We can assign only IPrincipal object

  >>> owner.owner = object()
  Traceback (most recent call last):
  ...
  ValueError: IPrincipal object is required.


Group owner

  >>> from zope.security.interfaces import IGroup
  >>> interface.directlyProvides(principal1, IGroup)

  >>> owner = IOwnership(content)
  >>> owner.owner = principal1

  >>> owner = IOwnership(content)
  >>> owner.isGroup
  True

  >>> interface.directlyProvides(content, IOwnerGroupAware)

  >>> grantinfo = IExtendedGrantInfo(content)
  >>> grantinfo.getRolesForPrincipal('bob')
  [('content.GroupOwner', PermissionSetting: Allow)]

  >>> grantinfo.getPrincipalsForRole('content.GroupOwner')
  [('bob', PermissionSetting: Allow)]

  >>> grantinfo.getPrincipalsForRole('unknown.Role')
  []

  >>> grantinfo.getRolesForPrincipal('meg')
  [('content.GroupOwner', PermissionSetting: Deny)]

  >>> interface.alsoProvides(content, IInheritOwnership)
  >>> grantinfo.getRolesForPrincipal('meg')
  []
