The tokenpolicy package supplies a modified sharing policy that honors tokens
from the zope.locking package.

-----------
Basic Setup
-----------

To test the tokenpolicy code, we need an object that may be locked and
shared.  This effectively means an object that can be adapted to
zope.app.keyreference.interfaces.IKeyReference,
that can be adapted to zope.app.annotation.interfaces.IAnnotations, and that
implements zc.sharing.interfaces.ISharable and
zope.app.annotation.interfaces.IAnnotatable.  Our first step will be to create
a factory for some demonstration objects that meet these requirements.

    >>> from zope import interface, component
    >>> import zc.sharing.interfaces
    >>> import zope.annotation.interfaces
    >>> import zope.annotation.attribute
    >>> import zope.app.keyreference.interfaces
    >>> class IDemo(interface.Interface):
    ...     """a demonstration interface for a demonstration class"""
    ...
    >>> class Demo(object):
    ...     interface.implements(
    ...         zc.sharing.interfaces.ISharable,
    ...         zope.annotation.interfaces.IAttributeAnnotatable,
    ...         IDemo)
    ...
    >>> component.provideAdapter(
    ...     zope.annotation.attribute.AttributeAnnotations)
    >>> class DemoKeyReference(object):
    ...     component.adapts(IDemo)
    ...     _class_counter = 0
    ...     interface.implements(
    ...         zope.app.keyreference.interfaces.IKeyReference)
    ...     def __init__(self, context):
    ...         self.context = context
    ...         class_ = type(self)
    ...         self._id = getattr(context, '__demo_key_reference__', None)
    ...         if self._id is None:
    ...             self._id = class_._class_counter
    ...             context.__demo_key_reference__ = self._id
    ...             class_._class_counter += 1
    ...     key_type_id = 'zope.locking.README.DemoKeyReference'
    ...     def __call__(self):
    ...         return self.context
    ...     def __hash__(self):
    ...         return (self.key_type_id, self._id)
    ...     def __cmp__(self, other):
    ...         if self.key_type_id == other.key_type_id:
    ...             return cmp(self._id, other._id)
    ...         return cmp(self.key_type_id, other.key_type_id) 
    ...
    >>> component.provideAdapter(DemoKeyReference)

We also need to provide adapters to the ISharing interfaces.

    >>> import zc.sharing.sharing
    >>> component.provideAdapter(zc.sharing.sharing.BaseSharing)
    >>> component.provideAdapter(zc.sharing.sharing.Sharing)

Additional setup is that you need to define privileges and lock privileges.
We'll assume this has been done already, defining Read at id 0, Write at id 2,
and Share at id 4; and defining the lock privileges as being a set of a single
privilege, Write/2.  (For test purposes, these are defined in tests.py.)

>>> demo = Demo()
>>> sharing = zc.sharing.interfaces.ISharing(demo)

-------------------------------------
Security Policy and zope.locking Tokens
-------------------------------------

This package includes a simple change to the sharing policy that checks for
the zope.locking token utility and disallows access to privileges registered
in zc.tokenpolicy.policy if a token exists for the object and none of the
security identifiers (user id and group id) for each principal in the
interaction are members of the token. This enables the tokenpolicy package to
be used as an enforcement mechanism for lock and freeze tokens in the
zope.locking package.

More interesting and flexible policies could be assembled.  One might allow
multiple token utilities, each managing a different set of privileges. 
Another might supply alternate tokens, so that a read lock token would have a
different meaning to the security policy than a write lock token.  These
possibilities are unexplored at the moment because a simpler solution is
sufficient for the current use cases.

To use the provided policy, you must define privileges that are controlled by
the tokens.  This is usually done with ZCML.  The ZCML directives
(see zcml.txt) themselves rely on five functions in the policy module:
definePrivilege, definePrivilegesByTitle, getPrivileges, getPrivilegeTitles,
and removePrivilege.

    >>> import zc.sharing.sharing
    >>> from zc.tokenpolicy import policy
    >>> sorted(policy.getPrivileges())
    []
    >>> policy.definePrivilege(2)
    >>> sorted(policy.getPrivileges())
    [2]
    >>> policy.definePrivilege(0)
    >>> sorted(policy.getPrivileges())
    [0, 2]
    >>> policy.removePrivilege(2)
    >>> sorted(policy.getPrivileges())
    [0]
    >>> policy.definePrivilegesByTitle(
    ...     ('Read', 'Write', 'Share'))
    >>> sorted(policy.getPrivileges())
    [0, 2, 4]
    >>> sorted(policy.getPrivilegeTitles())
    [u'Read', u'Share', u'Write']
    >>> policy.removePrivilege(2)
    >>> policy.removePrivilege(4)
    >>> policy.removePrivilege(0)
    >>> sorted(policy.getPrivileges())
    []

We'll use just 'Write' as our token privilege.  We also need to do some other
setup: define some permissions mapped to our privileges, set up the policy,
set up an interaction for us to use, and set up the token utility.

    >>> policy.definePrivilege(2)
    >>> import zc.sharing.policy
    >>> zc.sharing.policy.permissionPrivilege('R1', 0)
    ... # R1 permission -> Read privilege
    >>> zc.sharing.policy.permissionPrivilege('W1', 2)
    ... # W1 permission -> Write privilege
    >>> zc.sharing.policy.permissionPrivilege('S1', 4)
    ... # S1 permission -> Share privilege
    >>> import zope.security.management
    >>> oldPolicy = zope.security.management.setSecurityPolicy(
    ...     policy.SecurityPolicy)

    >>> class Principal:
    ...     def __init__(self, id):
    ...         self.id = id
    ...         self.groups = []
  
    >>> joe = Principal('joe')
    >>> class Participation:
    ...     interaction = None
    >>> participation = Participation()
    >>> participation.principal = joe
    >>> zope.security.management.endInteraction()
    >>> zope.security.management.newInteraction(participation)
    >>> interaction = zope.security.management.getInteraction()
    
    >>> import zope.locking.utility
    >>> import zope.locking.interfaces
    >>> util = zope.locking.utility.TokenUtility()
    >>> component.provideUtility(
    ...     util,
    ...     provides=zope.locking.interfaces.ITokenUtility)
    >>> import zope.component.interfaces
    >>> @interface.implementer(zope.component.interfaces.IComponentLookup)
    ... @component.adapter(interface.Interface)
    ... def siteManager(obj):
    ...     return component.getGlobalSiteManager()
    ...
    >>> component.provideAdapter(siteManager)

Let's give Joe the 'Read' and 'Write' privileges on the demo object.

    >>> sharing.setPrivileges('joe', ('Read', 'Write'))

Now, if we currently ask if joe has the 'W1' permission--part of the Write
privilege--on demo, he can:

    >>> interaction.checkPermission('W1', demo)
    True

If we freeze the object, though, he shouldn't have the permission, though.

    >>> from zope.locking.tokens import EndableFreeze
    >>> token = util.register(EndableFreeze(demo))
    >>> interaction.checkPermission('W1', demo)
    True

But he did!  Why?  Because of caching, of course.

    >>> interaction.invalidateCache()
    >>> interaction.checkPermission('W1', demo)
    False

The cache invalidation is fairly annoying, and easy to forget. This suggests
that we should perhaps invalidate the interaction cache whenever we get a
locking event.  This package includes a subscriber to do just that.

This won't catch tokens that expire in the middle of a transaction: we assume
that our transactions won't be long enough for that to be a serious problem. 
If that were not sufficient, you would need trickier solutions.  In any case,
let's register the handler.

    >>> from zc.tokenpolicy import subscribers
    >>> component.provideHandler(subscribers.tokenSubscriber)

That means we won't need to call invalidateCache for any of the other
examples.

So, Joe doesn't have the W1 permission because of the freeze token.  He still
has permissions not blocked by the token, though.

    >>> interaction.checkPermission('R1', demo)
    True

Missing permissions still are missing, of course.

    >>> interaction.checkPermission('S1', demo)
    False

When the token ends, joe regains access to W1.

    >>> token.end()
    >>> interaction.checkPermission('W1', demo)
    True

If there's an active token that joe is a part of, he can access the object
after all.

    >>> from zope.locking.tokens import SharedLock
    >>> token = util.register(SharedLock(demo, ('mary', 'joe')))
    >>> interaction.checkPermission('W1', demo)
    True

Importantly, participation in the token is simply a mask, and does not grant
access when there is none.  For instance, if we take the Write privilege away
from joe, the lock token won't get him anything.

    >>> sharing.removePrivileges('joe', ('Write',))
    >>> interaction.checkPermission('W1', demo)
    False

Now we'll give him the privilege back, but take him out of the lock.  No
permission.

    >>> sharing.addPrivileges('joe', ('Write',))
    >>> interaction.checkPermission('W1', demo)
    True
    >>> token.remove(('joe',))
    >>> interaction.checkPermission('W1', demo)
    False

If we add him back, he has it, and if we end the token he has it.  It's pretty
simple.

    >>> token.add(('joe',))
    >>> interaction.checkPermission('W1', demo)
    True
    >>> token.end()
    >>> interaction.checkPermission('W1', demo)
    True

    >>> discard = zope.security.management.setSecurityPolicy(oldPolicy)
    >>> zope.security.management.restoreInteraction()
