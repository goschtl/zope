The objectpolicy package makes it easy to override the default
zope.securitypolicy.zopepolicy on an object by object basis.

By default all objects use the zopepolicy. Objects that want to have
their own policy should have a marker interface `IObjectPolicyMarker`
and have an adapter to `IObjectPolicy`.

------
Levels
------

There are two levels supported.

- The low level is the SecurityMap.getCell level.
  Here are the permissions stored by principal or role.
  This works also with ZopePolicy as the security policy.
  Uses Allow, Deny, Unset values.
  Permissions descend (with ZopePolicy) to child objects or views.
  See:

  - IObjectPolicy.getPrincipalPermission
  - IObjectPolicy.getRolePermission
  - lowlevel.txt

  Installation:
  Drop the z3c.objectpolicy-configure.zcml in the instance/etc folder.

- The high level is the ISecurityPolicy.checkPermission level.
  Here the permission is usually `summarized` for the principal by it's
  roles, groups and object parent/child relations.
  ZopePolicy has to be overridden by the ObjectsPolicy security policy.
  Permissions do not decend to child objects or views.
  Uses True -- access, False -- no access values.
  See:

  - IObjectPolicy.checkPermission
  - highlevel.txt

  Installation:
  Override ZopePolicy in the instance/etc/securitypolicy.zcml
