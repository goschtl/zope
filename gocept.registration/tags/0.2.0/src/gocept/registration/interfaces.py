##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""User self-registration interfaces. """

import zope.interface
import zope.schema


class IRegistrations(zope.interface.Interface):
    """Provide self-registration functionality.

    Registrations are done for users giving their email address and
    possibly more data.

    A registration requires confirmation by the user. For this we
    send an email containing a confirmation link to his address.

    Upon opening the link a RegistrationConfirmedEvent is sent out
    and the application can perform whatever is necessary to active
    the user's account.

    After the successful confirmation the intermediate registration
    object is deleted.

    """

    def register(email, data=None):
        """Create a new registration for the given email address and
        data.

        Sends out an ObjectAddedEvent for the newly created
        IRegistration object.

        """

    def confirm(hash):
        """Confirm the registration identified by the hash.

        If successful sends out an IRegistrationConfirmed event.

        """


class IEmailConfiguration(zope.interface.Interface):
    """Defines configuration data for sending registration-related emails."""

    addr_from = zope.schema.TextLine(
        title=u"The sender's name and email address.")

    confirmation_url = zope.schema.TextLine(
        title=u"A URL including a single '%s' which can be replaced "
              u"by the confirmation hash.")

    confirmation_template = zope.interface.Attribute(
        u"A string with an RFC 822 message. The string is required "
        u"to include %()s places for the variables `from`, `to`, and "
        u"`link`.")


class IConfirmationEmail(zope.interface.Interface):
    """An email to confirm a registration."""

    message = zope.interface.Attribute(
        "A string containing an RFC 2822 message.")


class IRegistration(zope.interface.Interface):
    """A registration."""

    hash = zope.schema.BytesLine(
        title=u"A hash identifying this registration",)

    email = zope.schema.TextLine(
        title=u"The email for sending the confirmation mail to.")

    data = zope.interface.Attribute(
        u"Application-specific registration data.")


class IRegistrationConfirmed(zope.interface.Interface):

    registration = zope.schema.Object(
        title=u"The registration that was confirmed.",
        schema=IRegistration)


class RegistrationConfirmedEvent(object):

    zope.interface.implements(IRegistrationConfirmed)

    def __init__(self, registration):
        self.registration = registration
