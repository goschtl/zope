================================
Pluggable-Authentication Utility
================================

The Pluggable-Authentication Utility provides a framework for
authenticating principals and associating information with them.  It uses a
variety of different utilities, called plugins, and subscribers to get its
work done.

Authentication
==============

The primary job of an authentication utility is to authenticate principals.
Given a request object, the authentication utility returns a principal object,
if it can.  The pluggable-authentication utility does this in two steps:

1. It determines a principal ID based on authentication credentials found in a
   request, and then

2. It constructs a principal from the given ID, combining information from a
   number of sources.

It uses plug-ins in both phases of its work. Plugins are named utilities that
the utility is configured to use in some order.

In the first phase, the pluggable-authentication utility iterates
through a sequence of extractor plugins.  From each plugin, it
attempts to get a set of credentials.  If it gets credentials, it
iterates through a sequence of authentication plugins, trying to get a
principal id for the given credentials.  It continues this until it
gets a principal id.

Once it has a principal id, it begins the second phase.  In the second phase,
it iterates through a collection of principal-factory plugins until a plugin
returns a principal object for given principal ID.

When a factory creates a principal, it publishes a principal-created event.
Subscribers to this event are responsible for adding data, especially groups,
to the principal.  Typically, if a subscriber adds data, it should also add
corresponding interface declarations.

Let's look at an example. We create a simple plugin that provides credential
extraction:

  >>> from zope import interface
  >>> from zope.app.authentication import interfaces

  >>> class MyExtractor:
  ...
  ...     interface.implements(interfaces.IExtractionPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         return request.get('credentials')

We need to register this as a utility. Normally, we'd do this in ZCML. For the
example here, we'll use the `provideUtility()` function from
`zope.component`:

  >>> from zope.component import provideUtility
  >>> provideUtility(MyExtractor(), name='emy')

Now we also create an authenticator plugin that knows about object 42:

  >>> class Auth42:
  ...
  ...     interface.implements(interfaces.IAuthenticationPlugin)
  ...
  ...     def authenticateCredentials(self, credentials):
  ...         if credentials == 42:
  ...             return '42', {'domain': 42}

  >>> provideUtility(Auth42(), name='a42')

We provide a principal factory plugin:

  >>> class Principal:
  ...
  ...     description = title = ''
  ...
  ...     def __init__(self, id):
  ...         self.id = id
  ...
  ...     def __repr__(self):
  ...         return 'Principal(%r, %r)' % (self.id, self.title)

  >>> from zope.event import notify
  >>> class PrincipalFactory:
  ...
  ...     interface.implements(interfaces.IPrincipalFactoryPlugin)
  ...
  ...     def createAuthenticatedPrincipal(self, id, info, request):
  ...         principal = Principal(id)
  ...         notify(interfaces.AuthenticatedPrincipalCreated(
  ...                     principal, info, request))
  ...         return principal
  ...
  ...     def createFoundPrincipal(self, id, info):
  ...         principal = Principal(id)
  ...         notify(interfaces.FoundPrincipalCreated(principal, info))
  ...         return principal

  >>> provideUtility(PrincipalFactory(), name='pf')

Finally, we create a pluggable-authentication utility instance:

  >>> from zope.app import authentication
  >>> auth = authentication.LocalPluggableAuthentication()

Now, we'll create a request and try to authenticate:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(credentials=42)
  >>> auth.authenticate(request)

We don't get anything. Why?  Because we haven't configured the authentication
utility to use our plugins. Let's fix that:

  >>> auth.extractors = ('emy', )
  >>> auth.authenticators = ('a42', )
  >>> auth.factories = ('pf', )
  >>> principal = auth.authenticate(request)
  >>> principal
  Principal('42', '')

In addition to getting a principal, an `IPrincipalCreated` event will
have been generated.  We'll use the testing event logging API to see that 
this is the case:

  >>> from zope.app.event.tests.placelesssetup import getEvents, clearEvents

  >>> [event] = getEvents(interfaces.IAuthenticatedPrincipalCreated)

The event's principal is set to the principal:

  >>> event.principal is principal
  True

its info is set to the information returned by the authenticator:

  >>> event.info
  {'domain': 42}

and it's request set to the request we created:

  >>> event.request is request
  True

Normally, we provide subscribers to these events that add additional
information to the principal. For examples, we'll add one that sets
the title to a repr of the event info:

  >>> def add_info(event):
  ...     event.principal.title = `event.info`

  >>> from zope.app.tests.ztapi import subscribe
  >>> subscribe([interfaces.IPrincipalCreated], None, add_info)

Now, if we authenticate a principal, its title will be set:

  >>> auth.authenticate(request)
  Principal('42', "{'domain': 42}")

We can supply multiple plugins. For example, let's override our
authentication plugin:

  >>> class AuthInt:
  ...
  ...     interface.implements(interfaces.IAuthenticationPlugin)
  ...
  ...     def authenticateCredentials(self, credentials):
  ...         if isinstance(credentials, int):
  ...             return str(credentials), {'int': credentials}

  >>> provideUtility(AuthInt(), name='aint')

If we put it before the original authenticator:

  >>> auth.authenticators = 'aint', 'a42'

Then it will override the original:

  >>> auth.authenticate(request)
  Principal('42', "{'int': 42}")

But if we put it after, the original will be used:

  >>> auth.authenticators = 'a42', 'aint'
  >>> auth.authenticate(request)
  Principal('42', "{'domain': 42}")

But we'll fall back to the new one:

  >>> request = TestRequest(credentials=1)
  >>> auth.authenticate(request)
  Principal('1', "{'int': 1}")

As with with authenticators, we can specify multiple extractors:

  >>> class OddExtractor:
  ...
  ...     interface.implements(interfaces.IExtractionPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         credentials = request.get('credentials')
  ...         if isinstance(credentials, int) and (credentials%2):
  ...             return 1

  >>> provideUtility(OddExtractor(), name='eodd')
  >>> auth.extractors = 'eodd', 'emy'

  >>> request = TestRequest(credentials=41)
  >>> auth.authenticate(request)
  Principal('1', "{'int': 1}")

  >>> request = TestRequest(credentials=42)
  >>> auth.authenticate(request)
  Principal('42', "{'domain': 42}")

And we can specify multiple factories:

  >>> class OddPrincipal(Principal):
  ...
  ...     def __repr__(self):
  ...         return 'OddPrincipal(%r, %r)' % (self.id, self.title)

  >>> class OddFactory:
  ...
  ...     interface.implements(interfaces.IPrincipalFactoryPlugin)
  ...
  ...     def createAuthenticatedPrincipal(self, id, info, request):
  ...         i = info.get('int')
  ...         if not (i and (i%2)):
  ...             return None
  ...         principal = OddPrincipal(id)
  ...         notify(interfaces.AuthenticatedPrincipalCreated(
  ...                     principal, info, request))
  ...         return principal
  ...
  ...     def createFoundPrincipal(self, id, info):
  ...         i = info.get('int')
  ...         if not (i and (i%2)):
  ...             return None
  ...         principal = OddPrincipal(id)
  ...         notify(interfaces.FoundPrincipalCreated(
  ...                     principal, info))
  ...         return principal

  >>> provideUtility(OddFactory(), name='oddf')

  >>> auth.factories = 'oddf', 'pf'

  >>> request = TestRequest(credentials=41)
  >>> auth.authenticate(request)
  OddPrincipal('1', "{'int': 1}")

  >>> request = TestRequest(credentials=42)
  >>> auth.authenticate(request)
  Principal('42', "{'domain': 42}")

In this example, we used the supplemental information to get the
integer credentials.  It's common for factories to decide whether they
should be used depending on supplemental information.  Factories
should not try to inspect the principal ids. Why? Because, as we'll
see later, the pluggable-authentication utility may modify ids before
giving them to factories.  Similarly, subscribers should use the
supplemental information for any data they need.

Get a principal given an id
===========================

We can ask the pluggable-authentication utility for a principal, given an id.

To do this, the pluggable-authentication utility uses principal search
plugins:

  >>> class Search42:
  ...
  ...     interface.implements(interfaces.IPrincipalSearchPlugin)
  ...
  ...     def principalInfo(self, principal_id):
  ...         if principal_id == '42':
  ...             return {'domain': 42}

  >>> provideUtility(Search42(), name='s42')

  >>> class IntSearch:
  ...
  ...     interface.implements(interfaces.IPrincipalSearchPlugin)
  ...
  ...     def principalInfo(self, principal_id):
  ...         try:
  ...             i = int(principal_id)
  ...         except ValueError:
  ...             return None
  ...         if (i >= 0 and i < 100):
  ...             return {'int': i}

  >>> provideUtility(IntSearch(), name='sint')

  >>> auth.searchers = 's42', 'sint'

  >>> auth.getPrincipal('41')
  OddPrincipal('41', "{'int': 41}")

In addition to returning a principal, this will generate an event:

  >>> clearEvents()
  >>> auth.getPrincipal('42')
  Principal('42', "{'domain': 42}")

  >>> [event] = getEvents(interfaces.IPrincipalCreated)
  >>> event.principal
  Principal('42', "{'domain': 42}")

  >>> event.info
  {'domain': 42}

Our pluggable-authentication utility will not find a principal with
the ID '123'. Therefore it will delegate to the next utility. To make
sure that it's delegated, we put in place a fake utility.

  >>> from zope.app.utility.utility import testingNextUtility
  >>> from zope.app.security.interfaces import IAuthentication

  >>> class FakeAuthUtility:
  ...
  ...     interface.implements(IAuthentication)
  ...
  ...     lastGetPrincipalCall = lastUnauthorizedCall = None
  ...
  ...     def getPrincipal(self, name):
  ...         self.lastGetPrincipalCall = name
  ...
  ...     def unauthorized(self, id, request):
  ...         self.lastUnauthorizedCall = id

  >>> nextauth = FakeAuthUtility()
  >>> testingNextUtility(auth, nextauth, IAuthentication)

  >>> auth.getPrincipal('123')
  >>> nextauth.lastGetPrincipalCall
  '123'

Issuing a challenge
===================

If the unauthorized method is called on the pluggable-authentication
utility, the pluggable-authentication utility iterates through a
sequence of challenge plugins calling their challenge methods until
one returns True, indicating that a challenge was issued. (This is a
simplification. See "Protocols" below.)

Nothing will happen if there are no plugins registered.

  >>> auth.unauthorized(42, request)

However, our next utility was asked:

  >>> 42 == nextauth.lastUnauthorizedCall
  True

What happens if a plugin is registered depends on the plugin.  Let's
create a plugin that sets a response header:

  >>> class Challenge:
  ...
  ...     interface.implements(interfaces.IChallengePlugin)
  ...
  ...     def challenge(self, requests, response):
  ...         response.setHeader('X-Unauthorized', 'True')
  ...         return True

  >>> provideUtility(Challenge(), name='c')
  >>> auth.challengers = ('c', )

Now if we call unauthorized:

  >>> auth.unauthorized(42, request)

the response `X-Unauthorized` is set:

  >>> request.response.getHeader('X-Unauthorized')
  'True'

How challenges work in Zope 3
-----------------------------

To understand how the challenge plugins work, it's helpful to
understand how the unauthorized method of authentication services
get called.

If an 'Unauthorized' exception is raised and not caught by application
code, then the following things happen:

1. The current transaction is aborted.

2. A view is looked up for the exception.

3. The view gets the authentication utility and calls it's
   'unauthorized' method.

4. The pluggable-authentication utility will call its challenge
   plugins.  If none return a value, then the pluggable-authentication
   utility delegates to the next authentication utility above it in
   the containment hierarchy, or to the global authentication utility.

5. The view sets the body of the response.

Protocols
---------

Sometimes, we want multiple challengers to work together.  For
example, the HTTP specification allows multiple challenges to be issued
in a response.  A challenge plugin can provide a `protocol`
attribute.  If multiple challenge plugins have the same protocol,
then, if any of them are called and return True, then they will all be
called.  Let's look at an example.  We'll define two challengers that
add challenges to a X-Challenges headers:

  >>> class ColorChallenge:
  ...     interface.implements(interfaces.IChallengePlugin)
  ...
  ...     protocol = 'bridge'
  ...
  ...     def challenge(self, requests, response):
  ...         challenge = response.getHeader('X-Challenge', '')
  ...         response.setHeader('X-Challenge',
  ...                            challenge + 'favorite color? ')
  ...         return True

  >>> provideUtility(ColorChallenge(), name='cc')
  >>> auth.challengers = 'cc, ', 'c'

  >>> class BirdChallenge:
  ...     interface.implements(interfaces.IChallengePlugin)
  ...
  ...     protocol = 'bridge'
  ...
  ...     def challenge(self, requests, response):
  ...         challenge = response.getHeader('X-Challenge', '')
  ...         response.setHeader('X-Challenge',
  ...                            challenge + 'swallow air speed? ')
  ...         return True

  >>> provideUtility(BirdChallenge(), name='bc')
  >>> auth.challengers = 'cc', 'c', 'bc'

Now if we call unauthorized:

  >>> request = TestRequest(credentials=42)
  >>> auth.unauthorized(42, request)

the response `X-Unauthorized` is not set:

  >>> request.response.getHeader('X-Unauthorized')

But the X-Challenge header has been set by both of the new challengers
with the bridge protocol:

  >>> request.response.getHeader('X-Challenge')
  'favorite color? swallow air speed? '

Of course, if we put the original challenge first:

  >>> auth.challengers = 'c', 'cc', 'bc'
  >>> request = TestRequest(credentials=42)
  >>> auth.unauthorized(42, request)

We get 'X-Unauthorized' but not 'X-Challenge':

  >>> request.response.getHeader('X-Unauthorized')
  'True'
  >>> request.response.getHeader('X-Challenge')

Issuing challenges during authentication
----------------------------------------

During authentication, extraction and authentication plugins can raise
an 'Unauthorized' exception to indicate that a challenge should be
issued immediately. They might do this if they recognize partial
credentials that pertain to them.

Pluggable-Authentication Prefixes
=================================

Principal ids are required to be unique system wide.  Plugins will
often provide options for providing id prefixes, so that different
sets of plugins provide unique ids within a pluggable-authentication
utility.  If there are multiple pluggable-authentication utilities in
a system, it's a good idea to give each pluggable-authentication
utility a unique prefix, so that principal ids from different
pluggable-authentication utilities don't conflict. We can provide a
prefix when a pluggable-authentication utility is created:

  >>> auth = authentication.PluggableAuthentication('mypas_')
  >>> auth.extractors = 'eodd', 'emy'
  >>> auth.authenticators = 'a42', 'aint'
  >>> auth.factories = 'oddf', 'pf'
  >>> auth.searchers = 's42', 'sint'

Now, we'll create a request and try to authenticate:

  >>> request = TestRequest(credentials=42)
  >>> principal = auth.authenticate(request)
  >>> principal
  Principal('mypas_42', "{'domain': 42}")

Note that now, our principal's id has the pluggable-authentication
utility prefix.

We can still lookup a principal, as long as we supply the prefix:

  >>> auth.getPrincipal('mypas_42')
  Principal('mypas_42', "{'domain': 42}")

  >>> auth.getPrincipal('mypas_41')
  OddPrincipal('mypas_41', "{'int': 41}")

Searching
=========

As their name suggests, search plugins provide searching support.
We've already seen them used to get principals given principal
ids. They're also used to find principals given search criteria.

Different search plugins are likely to use very different search
criteria.  There are two approaches a plugin can use to support
searching:

- A plugin can provide IQuerySchemaSearch, in addition to
  `IPrincipalSearchPlugin`.  In this case, the plugin provides a search
  method and a schema that describes the input to be provided to the
  search method.

- For browser-based applications, the plugin can provide a browser
  view that provides
  `zope.app.form.browser.interfaces.ISourceQueryView`.

Pluggable-authentication utilities use search plugins in a very simple
way.  They merely implements
`zope.schema.interfaces.ISourceQueriables`:

  >>> [id for (id, queriable) in auth.getQueriables()]
  ['s42', 'sint']
  >>> [queriable.__class__.__name__
  ...  for (id, queriable) in auth.getQueriables()]
  ['Search42', 'IntSearch']

Design Notes
============

- It is common for the same component to implement authentication and
  search or extraction and challenge. See
  `ISearchableAuthenticationPlugin` and
  `IExtractionAndChallengePlugin`.

Special groups
==============

Two special groups, Authenticated, and Everyone may apply to users
created by the pluggable-authentication utility.  There is a
subscriber, specialGroups, that will set these groups on any non-group
principals if IAuthenticatedGroup, or IEveryoneGroup utilities are
provided.

Lets define a group-aware principal:

    >>> import zope.security.interfaces
    >>> class GroupAwarePrincipal(Principal):
    ...     interface.implements(zope.security.interfaces.IGroupAwarePrincipal)
    ...     def __init__(self, id):
    ...         Principal.__init__(self, id)
    ...         self.groups = []

If we notify the subscriber with this principal, nothing will happen
because the groups haven't been defined:

    >>> prin = GroupAwarePrincipal('x')
    >>> event = interfaces.FoundPrincipalCreated(prin, {})
    >>> authentication.authentication.specialGroups(event)
    >>> prin.groups
    []

Now, if we define the Everybody group:

    >>> import zope.app.security.interfaces
    >>> class EverybodyGroup(Principal):
    ...     interface.implements(zope.app.security.interfaces.IEveryoneGroup)

    >>> everybody = EverybodyGroup('all')
    >>> provideUtility(everybody)
    
Then the group will be added to the principal:

    >>> authentication.authentication.specialGroups(event)
    >>> prin.groups
    ['all']

Similarly for the authenticated group:

    >>> class AuthenticatedGroup(Principal):
    ...     interface.implements(
    ...         zope.app.security.interfaces.IAuthenticatedGroup)

    >>> authenticated = AuthenticatedGroup('auth')
    >>> provideUtility(authenticated)
    
Then the group will be added to the principal:

    >>> prin.groups = []
    >>> authentication.authentication.specialGroups(event)
    >>> prin.groups.sort()
    >>> prin.groups
    ['all', 'auth']

These groups are only added to non-group principals:

    >>> prin.groups = []
    >>> interface.directlyProvides(prin, zope.security.interfaces.IGroup)
    >>> authentication.authentication.specialGroups(event)
    >>> prin.groups
    []

And they are only added to group aware principals:

    >>> prin = Principal('eek')
    >>> prin.groups = []
    >>> event = interfaces.FoundPrincipalCreated(prin, {})
    >>> authentication.authentication.specialGroups(event)
    >>> prin.groups
    []
