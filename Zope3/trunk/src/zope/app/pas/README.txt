================================
Pluggable Authentication Service
================================

The Pluggable Authentication Service (PAS) provides a framework for
authenticating principals and associating information with them.  It
uses a variety of different utilities, called plugins, and subscribers
to get its work done.

Authentication
==============

The primary job of an authentication service is to authenticate
principals.  Given a request object, the authentication service
returns a principal object, if it can.  The PAS does this in two
steps:

1. It determines a principal ID based on authentication credentials
   found in a request, and then

2. It constructs a principal from the given ID, combining information
   from a number of sources.

It uses plug-ins in both phases of its work. Plugins are named
utilities that the service is configured to use in some order.

In the first phase, the PAS iterates through a sequence of extractor
plugins.  From each plugin, it attempts to get a set of credentials.
If it gets credentials, it iterates through a sequence of authentication
plugins, trying to get a principal id for the given credentials.  It
continues this until it gets a principal id.

Once it has a principal id, it begins the second phase.  In the second
phase, it iterates through a collection of principal-factory plugins until a
plugin returns a principal object for given principal ID.

When a factory creates a principal, it publishes a principal-created
event.  Subscribers to this event are responsible for adding data,
especially groups, to the principal.  Typically, if a subscriber adds
data, it should also add corresponding interface declarations.

Let's look at an example. We create a simple plugin that provides
credential extraction:

  >>> import zope.interface
  >>> from zope.app.pas import interfaces

  >>> class MyExtractor:
  ...
  ...     zope.interface.implements(interfaces.IExtractionPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         return request.get('credentials')

We need to register this as a utility. Normally, we'd do this in
ZCML. For the example here, we'll use the provideUtility function from
`zope.app.tests.ztapi`:

  >>> from zope.app.tests.ztapi import provideUtility
  >>> provideUtility(interfaces.IExtractionPlugin, MyExtractor(), name='emy')

Now we also create an authenticator plugin that knows about object 42:

  >>> class Auth42:
  ...
  ...     zope.interface.implements(interfaces.IAuthenticationPlugin)
  ...
  ...     def authenticateCredentials(self, credentials):
  ...         if credentials == 42:
  ...             return '42', {'domain': 42}

  >>> provideUtility(interfaces.IAuthenticationPlugin, Auth42(), name='a42')

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
  ...     zope.interface.implements(interfaces.IPrincipalFactoryPlugin)
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

  >>> provideUtility(interfaces.IPrincipalFactoryPlugin, PrincipalFactory(), 
  ...                name='pf')

Finally, we create a PAS instance:

  >>> from zope.app import pas
  >>> service = pas.LocalPAS()

Now, we'll create a request and try to authenticate:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(credentials=42)
  >>> service.authenticate(request)

We don't get anything. Why?  Because we haven't configured the service
to use our plugins. Let's fix that:

  >>> service.extractors = ('emy', )
  >>> service.authenticators = ('a42', )
  >>> service.factories = ('pf', )
  >>> principal = service.authenticate(request)
  >>> principal
  Principal('42', '')

In addition to getting a principal, an IPASPrincipalCreated event will
have been generated.  We'll use an the testing event logging API to
see that this is the case:

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
  >>> subscribe([interfaces.IPASPrincipalCreated], None, add_info)

Now, if we authenticate a principal, its title will be set:

  >>> service.authenticate(request)
  Principal('42', "{'domain': 42}")

We can supply multiple plugins. For example, let's override our
authentication plugin:

  >>> class AuthInt:
  ...
  ...     zope.interface.implements(interfaces.IAuthenticationPlugin)
  ...
  ...     def authenticateCredentials(self, credentials):
  ...         if isinstance(credentials, int):
  ...             return str(credentials), {'int': credentials}

  >>> provideUtility(interfaces.IAuthenticationPlugin, AuthInt(), name='aint')

If we put it before the original authenticator:

  >>> service.authenticators = 'aint', 'a42'

Then it will override the original:

  >>> service.authenticate(request)
  Principal('42', "{'int': 42}")

But if we put it after, the original will be used:

  >>> service.authenticators = 'a42', 'aint'
  >>> service.authenticate(request)
  Principal('42', "{'domain': 42}")

But we'll fall back to the new one:

  >>> request = TestRequest(credentials=1)
  >>> service.authenticate(request)
  Principal('1', "{'int': 1}")

As with with authenticators, we can specify multiple extractors:

  >>> class OddExtractor:
  ...
  ...     zope.interface.implements(interfaces.IExtractionPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         credentials = request.get('credentials')
  ...         if isinstance(credentials, int) and (credentials%2):
  ...             return 1

  >>> provideUtility(interfaces.IExtractionPlugin, OddExtractor(), name='eodd')
  >>> service.extractors = 'eodd', 'emy'
 
  >>> request = TestRequest(credentials=41)
  >>> service.authenticate(request)
  Principal('1', "{'int': 1}")

  >>> request = TestRequest(credentials=42)
  >>> service.authenticate(request)
  Principal('42', "{'domain': 42}")

And we can specify multiple factories:

  >>> class OddPrincipal(Principal):
  ...
  ...     def __repr__(self):
  ...         return 'OddPrincipal(%r, %r)' % (self.id, self.title)

  >>> class OddFactory:
  ...
  ...     zope.interface.implements(interfaces.IPrincipalFactoryPlugin)
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

  >>> provideUtility(interfaces.IPrincipalFactoryPlugin, OddFactory(), 
  ...                name='oddf')

  >>> service.factories = 'oddf', 'pf'
 
  >>> request = TestRequest(credentials=41)
  >>> service.authenticate(request)
  OddPrincipal('1', "{'int': 1}")
 
  >>> request = TestRequest(credentials=42)
  >>> service.authenticate(request)
  Principal('42', "{'domain': 42}")

In this example, we used the supplemental information to get the
integer credentials.  It's common for factories to decide whether they
should be used depending on supplemental information.  Factories
should not try to inspect the principal ids. Why? Because, as we'll
see later, the PAS may modify ids before giving them to factories.
Similarly, subscribers should use the supplemental information for any
data they need.

Get a principal given an id
===========================

We can ask the PAS for a principal, given an id. 

To do this, the PAS uses principal search plugins:

  >>> class Search42:
  ...
  ...     zope.interface.implements(interfaces.IPrincipalSearchPlugin)
  ...
  ...     def get(self, principal_id):
  ...         if principal_id == '42':
  ...             return {'domain': 42}

  >>> provideUtility(interfaces.IPrincipalSearchPlugin, Search42(), 
  ...                name='s42')

  >>> class IntSearch:
  ...
  ...     zope.interface.implements(interfaces.IPrincipalSearchPlugin)
  ...
  ...     def get(self, principal_id):
  ...         try:
  ...             i = int(principal_id)
  ...         except ValueError:
  ...             return None
  ...         if (i >= 0 and i < 100):
  ...             return {'int': i}

  >>> provideUtility(interfaces.IPrincipalSearchPlugin, IntSearch(), 
  ...                name='sint')
 
  >>> service.searchers = 's42', 'sint'

  >>> service.getPrincipal('41')
  OddPrincipal('41', "{'int': 41}")

In addition to returning a principal, this will generate an event:

  >>> clearEvents()
  >>> service.getPrincipal('42')
  Principal('42', "{'domain': 42}")

  >>> [event] = getEvents(interfaces.IPASPrincipalCreated)
  >>> event.principal
  Principal('42', "{'domain': 42}")

  >>> event.info
  {'domain': 42}

Our PAS will not find a principal with the ID '123'. Therefore it will
delegate to the next service. To make sure that it's delegated, we put in place
a fake service.

  >>> from zope.app.component.localservice import testingNextService
  >>> from zope.app.site.interfaces import ISiteManager
  >>> from zope.app import servicenames

  >>> class FakeService:
  ...
  ...     zope.interface.implements(ISiteManager)
  ...
  ...     lastGetPrincipalCall = lastUnauthorizedCall = None
  ...
  ...     def getPrincipal(self, name):
  ...         self.lastGetPrincipalCall = name
  ...
  ...     def unauthorized(self, id, request):
  ...         self.lastUnauthorizedCall = id

  >>> nextservice = FakeService()
  >>> testingNextService(service, nextservice, servicenames.Authentication)

  >>> service.getPrincipal('123')
  >>> '123' == nextservice.lastGetPrincipalCall
  True

Issuing a challenge
===================

If the unauthorized method is called on the PAS, the PAS iterates
through a sequence of challenge plugins calling their challenge
methods until one returns True, indicating that a challenge was
issued. (This is a simplification. See "Protocols" below.)

Nothing will happen if there are no plugins registered.

  >>> service.unauthorized(42, request)

However, our next service was asked:

  >>> 42 == nextservice.lastUnauthorizedCall
  True

What happens if a plugin is registered depends on the plugin.  Let's
create a plugin that sets a response header:

  >>> class Challenge:
  ...     
  ...     zope.interface.implements(interfaces.IChallengePlugin)
  ...     
  ...     def challenge(self, requests, response):
  ...         response.setHeader('X-Unauthorized', 'True')
  ...         return True

  >>> provideUtility(interfaces.IChallengePlugin, Challenge(), name='c')
  >>> service.challengers = ('c', )

Now if we call unauthorized:

  >>> service.unauthorized(42, request)

the response `X-Unauthorized` is set:

  >>> request.response.getHeader('X-Unauthorized')
  'True'

How challenges work in Zope 3
-----------------------------

To understand how the challenge plugins work, it's helpful to
understand how the unauthorized method of authenticaton services 
get called.

If an 'Unauthorized' exception is raised and not caught by application
code, then the following things happen:

1. The current transaction is aborted.

2. A view is looked up for the exception.

3. The view gets the authentication service and calls it's
   'unauthorized' method.

4. The PAS will call its challenge plugins.  If none return a value,
   then the PAS delegates to the next authentication service above it
   in the containment hierarchy, or to the global authentication
   service.

5. The view sets the body of the response.

Protocols
---------

Sometimes, we want multiple challengers to work together.  For
example, the HTTP specification allows multiple challenges to be isued
in a response.  A challenge plugin can provide a `protocol`
attribute.  If multiple challenge plugins have the same protocol,
then, if any of them are called and return True, then they will all be
called.  Let's look at an example.  We'll define two challengers that
add challenges to a X-Challenges headers:

  >>> class ColorChallenge:
  ...     zope.interface.implements(interfaces.IChallengePlugin)
  ...     
  ...     protocol = 'bridge'
  ...     
  ...     def challenge(self, requests, response):
  ...         challenge = response.getHeader('X-Challenge', '')
  ...         response.setHeader('X-Challenge', 
  ...                            challenge + 'favorite color? ')
  ...         return True

  >>> provideUtility(interfaces.IChallengePlugin, ColorChallenge(), name='cc')
  >>> service.challengers = 'cc, ', 'c'

  >>> class BirdChallenge:
  ...     zope.interface.implements(interfaces.IChallengePlugin)
  ...     
  ...     protocol = 'bridge'
  ...     
  ...     def challenge(self, requests, response):
  ...         challenge = response.getHeader('X-Challenge', '')
  ...         response.setHeader('X-Challenge', 
  ...                            challenge + 'swallow air speed? ')
  ...         return True

  >>> provideUtility(interfaces.IChallengePlugin, BirdChallenge(), name='bc')
  >>> service.challengers = 'cc', 'c', 'bc'

Now if we call unauthorized:

  >>> request = TestRequest(credentials=42)
  >>> service.unauthorized(42, request)

the response `X-Unauthorized` is not set:

  >>> request.response.getHeader('X-Unauthorized')

But the X-Challenge header has been set by both of the new challengers
with the bridge protocol:

  >>> request.response.getHeader('X-Challenge')
  'favorite color? swallow air speed? '

Of course, if we put the original challenge first:

  >>> service.challengers = 'c', 'cc', 'bc'
  >>> request = TestRequest(credentials=42)
  >>> service.unauthorized(42, request)

We get 'X-Unauthorized' but not 'X-Challenge':

  >>> request.response.getHeader('X-Unauthorized')
  'True'
  >>> request.response.getHeader('X-Challenge')

Issuing challenges during authentication
----------------------------------------

During authentication, extraction and authentication plugins can raise
an 'Unauthorized' exception to indicate that a challenge should be
issued immediately. They might do this if the recognize partial
credentials that pertain to them.

PAS prefixes
============

Principal ids are required to be unique system wide.  Plugins will
often provide options for providing id prefixes, so that different
sets of plugins provide unique ids within a PAS.  If there are
multiple PASs in a system, it's a good idea to give each PAS a
unique prefix, so that principal ids from different PASs don't
conflict. We can provide a prefix when a PAS is created:

  >>> service = pas.PAS('mypas_')
  >>> service.extractors = 'eodd', 'emy'
  >>> service.authenticators = 'a42', 'aint'
  >>> service.factories = 'oddf', 'pf'
  >>> service.searchers = 's42', 'sint'

Now, we'll create a request and try to authenticate:

  >>> request = TestRequest(credentials=42)
  >>> principal = service.authenticate(request)
  >>> principal
  Principal('mypas_42', "{'domain': 42}")

Note that now, our principal's id has the PAS prefix.

We can still lookup a principal, as long as we supply the prefix:

  >>> service.getPrincipal('mypas_42')
  Principal('mypas_42', "{'domain': 42}")

  >>> service.getPrincipal('mypas_41')
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
  `IPrincipalSearchPlugin`.  In this case, the plugin provises a search
  method and a schema that describes the input to be provided to the
  search method.

- For browser-based applications, the plugin can provide a browser
  view that provides
  `zope.app.form.browser.interfaces.ISourceQueryView`.

PAS uses search plugins in a very simple way.  It mearly implements
`zope.schema.interfaces.ISourceQueriables`:

  >>> [id for (id, queriable) in service.getQueriables()]
  ['s42', 'sint']
  >>> [queriable.__class__.__name__ 
  ...  for (id, queriable) in service.getQueriables()]
  ['Search42', 'IntSearch']

Design Notes
============

- It is common for the same component to implement authentication and
  search or extraction and challenge. See
  `ISearchableAuthenticationPlugin` and
  `IExtractionAndChallengePlugin`.
 
