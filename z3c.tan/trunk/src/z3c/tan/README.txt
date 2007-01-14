=================================
Transaction Authorization Numbers
=================================

A Transaction Authorization Number, short TAN, is a security feature to give a
principal additional permissions for a limited amount of time, either one
transaction or a short time span, like a day or a week.

This package implements a TAN system as a plugin to the authentication utility
in ``zope.app.authentication``. A TAN is simply a group. Roles and permissions
are granted to the TAN group representing the additional access a principal
will have when s/he entered the TAN. When the principal is created at the
beginning of a request, an event listener extracts the TAN from the request
and adds the TAN group to the principal's groups, if it is aware of groups.


Setup
=====

Before we can start explaining this package, we have to bring up the
authentication utility:

  >>> from zope.app.folder import Folder, rootFolder
  >>> root = rootFolder()

  >>> from zope.app.testing import setup
  >>> sm = setup.createSiteManager(root, True)

  >>> from zope.app.authentication import authentication
  >>> from zope.app.security.interfaces import IAuthentication
  >>> pau = authentication.PluggableAuthentication('auth.')
  >>> sm['default']['auth'] = pau
  >>> sm.registerUtility(pau, IAuthentication)

  >>> from zope.app.authentication import principalfolder
  >>> pau[u'users'] = principalfolder.PrincipalFolder('users.')
  >>> pau.authenticatorPlugins += (u'users',)

  >>> import zope.component
  >>> zope.component.provideAdapter(
  ...     principalfolder.FoundPrincipalFactory)
  >>> zope.component.provideAdapter(
  ...     principalfolder.AuthenticatedPrincipalFactory)


TAN Information
===============

A TAN is a very simple object and so is the TAN information:

  >>> from z3c.tan import tan
  >>> info1 = tan.TANInformation(u'T2581KL2')
  >>> info1
  <TANInformation u'T2581KL2'>

The first argument if the TAN object is the TAN itself.

  >>> info1.tan
  u'T2581KL2'

There is no title and description by default:

  >>> info1.title
  >>> info1.description

Optionally, you can specify the title and description in the constructor:

  >>> tan2 = tan.TANInformation(
  ...     u'HSI89S4G',
  ...     u'Transfer money',
  ...     u'This TAN is intended to transfer money to another account.')

  >>> tan2.tan
  u'HSI89S4G'
  >>> tan2.title
  u'Transfer money'
  >>> tan2.description
  u'This TAN is intended to transfer money to another account.'

Oftentimes you want to restrict a TAN to paricular principals. In this case
you can specify the list of allowed principals.

  >>> info1.allowedPrincipals

Initially the attribute is set to ``None``, meaning that all principals can
use the TAN. The allowed principals are a list of principal:

  >>> srichter = principalfolder.InternalPrincipal(
  ...     'srichter', 'foobar', 'Stephan Richter')
  >>> pau[u'users']['srichter'] = srichter

  >>> info1.allowedPrincipals = ('auth.users.srichter',)

Let's now have a look at how the TANs are manged.


TAN Managers
============

The TANs are managed by a TAN manager.

  >>> from z3c.tan import manager
  >>> tans = manager.TANManager('tans.')

The TAN manager is a container for the TAN information objects.

  >>> from zope.app.container.interfaces import IContainer
  >>> IContainer.providedBy(tans)
  True

  >>> tans.add(info1)
  >>> sorted(tans.items())
  [(u'T2581KL2', <TANInformation u'T2581KL2'>)]

  >>> tans.add(tan2)

Besides being a container, the TAN Manager is also an
``IAuthenticatorPlugin``:

  >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
  >>> IAuthenticatorPlugin.providedBy(tans)
  True

Let's see whether all the authenticator plugin methods work as expected. The
first method authenticates the creadentials. In this case the credentials is
the id:

  >>> tans.authenticateCredentials(u'T2581KL2')
  <TANInformation u'T2581KL2'>

  >>> tans.authenticateCredentials(u'FOO12345')

  >>> tans.authenticateCredentials({'login': 'foo', 'password': 'bar'})

You can also ask for the principal information directly:

  >>> tans.principalInfo('tans.T2581KL2')
  <TANInformation u'T2581KL2'>

  >>> tans.principalInfo(u'FOO12345')

Further, the TAN manager supports the searching:

  >>> from zope.app.authentication.interfaces import IQuerySchemaSearch
  >>> IQuerySchemaSearch.providedBy(tans)
  True

  >>> sorted(tans.search({'search': 'T2'}))
  [u'tans.T2581KL2']

Finally, you can never use a TAN twice. Let's create another TAN and add it to
the system:

  >>> tan3 = tan.TANInformation(u'HU1MHG60')
  >>> tans.add(tan3)

Next we remove the TAN:

  >>> del tans[tan3.tan]

If we try to add the TAN again, the system should deny the action by raising a
``TANAlreadyUsed`` error:

  >>> tans.add(tan3)
  Traceback (most recent call last):
  ...
  TANAlreadyUsed: HU1MHG60


TAN Assignment Subscriber
=========================

Whenever a principal is created not originating from a TAN but a login and
password, it must be checked whether a TAN has been specified and added as a
group, if necessary.

First we have to add the TAN Manager to the authentication service and register
it:

  >>> pau[u'tans'] = tans
  >>> pau.authenticatorPlugins += (u'tans',)

Next we have to create a principal created event:

  >>> from z3c.tan.tests import TestSession
  >>> zope.component.provideAdapter(TestSession)

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.app.authentication.interfaces import \
  ...     AuthenticatedPrincipalCreated

  >>> srichter = pau.getPrincipal('auth.users.srichter')
  >>> request = TestRequest()
  >>> event = AuthenticatedPrincipalCreated(pau, srichter, None, request)

In this first case no TAN was specified, so sending the event to the
subscriber should not yield a TAN group:

  >>> manager.assignTAN(event)
  >>> srichter.groups
  []

Now we create a new request that has the TAN information:

  >>> request = TestRequest(form={'login.tan': u'T2581KL2'})
  >>> event = AuthenticatedPrincipalCreated(pau, srichter, None, request)
  >>> manager.assignTAN(event)
  >>> srichter.groups
  [u'auth.T2581KL2']

Clean up the session, so we can start over again:

  >>> clearSessionData()


Credentials Extractor
=====================

This package also provides a session-based credentials extractor, so that the
TAN Manager can also be used for authentication. Let's check it out:

  >>> from z3c.tan import session
  >>> cred = session.SessionCredentialsPlugin()

First, the credentials must be extracted from the request. Of course, only
HTTP requests make sense here:

  >>> cred.extractCredentials(object())

  >>> cred.extractCredentials(TestRequest())

  >>> request = TestRequest(form={'login.tan': u'T2581KL2'})
  >>> cred.extractCredentials(request)
  u'T2581KL2'

  >>> cred.extractCredentials(TestRequest())
  u'T2581KL2'

If the authentication fails, the credentials plugin has a chance to create a
new challenge:

  >>> cred.challenge(object())
  False

  >>> request = TestRequest()
  >>> cred.challenge(request)
  True

  >>> request.response._headers
  {'location': ['http://127.0.0.1/@@tanEntry.html?camefrom=%2F']}

Logging out works basically means to end using the TAN.

  >>> from zope.app.session.interfaces import ISession
  >>> ISession(request)[session.SESSION_KEY]['tan']
  u'T2581KL2'

  >>> cred.logout(object())
  False

  >>> cred.logout(request)
  True

  >>> ISession(request)[session.SESSION_KEY]['tan']


Integration
===========

Let's now check the integration of the full authentication mechanism. First we
register the TAN assignment subscriber:

  >>> zope.component.provideHandler(manager.assignTAN)

We also have to add a credentials plugin for the users:

  >>> from zope.app.authentication.session import SessionCredentialsPlugin
  >>> pau[u'creds'] = SessionCredentialsPlugin()
  >>> pau.credentialsPlugins += (u'creds',)

Now we can authenticate the user:

  >>> request = TestRequest(form={'login': 'srichter', 'password': 'foobar'})
  >>> user = pau.authenticate(request)
  >>> user
  Principal(u'auth.users.srichter')
  >>> user.groups
  []

Now the user enters a TAN and submits it:

  >>> request = TestRequest(form={'login.tan': u'T2581KL2'})
  >>> user = pau.authenticate(request)
  >>> user
  Principal(u'auth.users.srichter')
  >>> user.groups
  [u'auth.T2581KL2']

Finally, we allow to authenticate withe w=only the TAN:

  >>> clearSessionData()

  >>> pau[u'tan-creds'] = cred
  >>> pau.credentialsPlugins += (u'tan-creds',)

  >>> request = TestRequest(form={'login.tan': u'T2581KL2'})
  >>> user = pau.authenticate(request)
  >>> user
  Principal(u'auth.tans.T2581KL2')
  >>> user.groups
  []


TAN Generator
=============

Usually, TANs want to be auto-generated. The TAN generator adds a certain
amount of TANs to a manager. You can also specify all the other attributes as
arguments to the generate method:

  >>> from z3c.tan import generator
  >>> gen = generator.CommonTANGenerator()

  >>> tans = manager.TANManager()
  >>> gen.generate(
  ...     tans,
  ...     amount=2,
  ...     title=u'Transfer Money',
  ...     description=u"Stephan's TANs to transfer money.",
  ...     allowedPrincipals=('auth.users.srichter',))
  [u'40OIQMX6', u'RU4QJXSH']

Let's now make sure that the attributes are set too:

  >>> tan4 = tans[u'40OIQMX6']
  >>> tan4
  <TANInformation u'40OIQMX6'>

  >>> tan4.id
  u'40OIQMX6'
  >>> tan4.tan
  u'40OIQMX6'
  >>> tan4.title
  u'Transfer Money'
  >>> tan4.description
  u"Stephan's TANs to transfer money."
  >>> tan4.allowedPrincipals
  ('auth.users.srichter',)


Conclusion
==========

The way TANs are implemented in this package, it is possible to use them as
free-standing principals that can be "logged in", but also as groups on a
principal.
