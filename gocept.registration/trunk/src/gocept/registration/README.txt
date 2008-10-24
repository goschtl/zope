======================
User self-registration
======================

Registering a user
==================

Registrations are managed by the registrations utility:

  >>> from gocept.registration.registrations import Registrations
  >>> registrations = Registrations()

We can now register a user by passing his email address and some additional
data:

  >>> peter = registrations.register('peter@example.com', {'name': u'Peter'})
  >>> peter
  <gocept.registration.registrations.Registration object at 0x...>

All registrations have a hash that anonymous identifies them, the email and
the data attached:

  >>> peter.hash
  '<SHA-HASH>'
  >>> peter.email
  'peter@example.com'
  >>> peter.data
  {'name': u'Peter'}

Peter's registration is contained in the utility identified by the hash:

  >>> registrations[peter.hash]
  <gocept.registration.registrations.Registration object at 0x...>

Peter can now confirm his registration using the hash that was given to him:

  >>> registrations.confirm(peter.hash)

Now that he confirmed his registration, it isn't stored in the utility
anymore:

  >>> registrations[peter.hash]
  Traceback (most recent call last):
  KeyError: '<SHA-HASH>'

Customizing the Registration Object
===================================

When calling the ``register`` method, we can also optionally pass in a
factory to construct the registration.  This is useful when
subclassing the ``Registration`` class.

  >>> from gocept.registration.registrations import Registration
  >>> class MyRegistration(Registration):
  ...     def __init__(self, hash, email, data):
  ...         assert data.has_key('agentNumber'), 'missing agent number!'
  ...         super(MyRegistration, self).__init__(hash, email, data)

  >>> registrations.register('james@bond.com',
  ...                        {'name': u'James Bond'},
  ...                        factory=MyRegistration)
  Traceback (most recent call last):
  ...
  AssertionError: missing agent number!
  >>> registrations.register('james@bond.com',
  ...                        {'name': u'James Bond',
  ...                         'agentNumber': u'007'},
  ...                        factory=MyRegistration)
  <MyRegistration object at ...>


Application hooks
=================

There are two hooks that applications can tap into for customizing the registration process:

- the ObjectAddedEvent for the registration object, and
- the RegistrationConfirmedEvent when the user confirms his registration

Let's register a subscriber for both events to demonstrate where each is called:

  >>> def registered(event):
  ...     print event, event.object
  >>> import zope.component
  >>> from zope.app.container.interfaces import IObjectAddedEvent
  >>> zope.component.provideHandler(registered, (IObjectAddedEvent,))

  >>> chuck = registrations.register('chuck@example.com', {'name': u'LeChuck'})
  <zope.app.container.contained.ObjectAddedEvent object at 0x...>
  <gocept.registration.registrations.Registration object at 0x...>

  >>> def confirmed(event):
  ...     print event, event.registration
  >>> from gocept.registration.interfaces import IRegistrationConfirmed
  >>> zope.component.provideHandler(confirmed, (IRegistrationConfirmed,))

  >>> registrations.confirm(chuck.hash)
  <gocept.registration.interfaces.RegistrationConfirmedEvent object at 0x...>
  <gocept.registration.registrations.Registration object at 0x...>

Let's clean those registrations up again:

  >>> from zope.app.testing import placelesssetup
  >>> placelesssetup.tearDown()


Confirmation emails
===================

Sending out registration emails is divided into two parts: creating the email
itself, and sending it.

Creating confirmation mails
---------------------------

To provide some central configuration, registrations can be adapted to
IRegistrationEmailConfiguration:

  >>> from gocept.registration.interfaces import IEmailConfiguration
  >>> from gocept.registration.interfaces import IRegistration
  >>> class TestConfig(object):
  ...     zope.interface.implements(IEmailConfiguration)
  ...     addr_from = "Ad Ministrator <admin@example.com>"
  ...     confirmation_url = "http://example.com/confirm?hash=%s"
  ...     confirmation_template = """From: %(from)s
  ... To: %(to)s
  ... Subject: Please confirm your registration
  ... 
  ... We received your registration. To activate it, please follow this confirmation
  ... 
  ... link:
  ... 
  ...  %(link)s"""
  ...     def __init__(self, registration):
  ...         pass
  >>> zope.component.provideAdapter(TestConfig, adapts=(IRegistration,))

The confirmation email is created by adapting the registration object to the
IRegistrationEmail interface. We provide a simple implementation to start
from.

  >>> from gocept.registration.email import ConfirmationEmail
  >>> mail = ConfirmationEmail(chuck)
  >>> print mail.message
  From: Ad Ministrator <admin@example.com>
  To: chuck@example.com
  Subject: Please confirm your registration
  <BLANKLINE>
  We received your registration. To activate it, please follow this confirmation
  link:
  <BLANKLINE>
  http://example.com/confirm?hash=<SHA-HASH>


Sending confirmation mails
--------------------------

We provide a standard event handler that will send out an email for the
registration:

  >>> from gocept.registration.email import send_registration_mail
  >>> zope.component.provideAdapter(ConfirmationEmail, (IRegistration,))
  >>> zope.component.provideHandler(send_registration_mail, (IRegistration, IObjectAddedEvent,))
  >>> from zope.component.event import objectEventNotify
  >>> zope.component.provideHandler(objectEventNotify, (IObjectAddedEvent,))
  >>> from gocept.registration.tests import DummyMailer
  >>> zope.component.provideUtility(DummyMailer())
  >>> janine = registrations.register('janine@example.com')
  (Ad Ministrator <admin@example.com> -> ['janine@example.com'])
  From: Ad Ministrator <admin@example.com>
  To: janine@example.com
  Subject: Please confirm your registration
  <BLANKLINE>
  We received your registration. To activate it, please follow this confirmation
  <BLANKLINE>
  link:
  <BLANKLINE>
  http://example.com/confirm?hash=<SHA-HASH>
