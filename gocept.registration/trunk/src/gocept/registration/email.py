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
"""Confirmation emails."""

import gocept.registration.interfaces
import zope.interface
import zope.app.container.interfaces


class ConfirmationEmail(object):
    """A basic confirmation email."""

    zope.component.adapts(
        gocept.registration.interfaces.IRegistration)

    zope.interface.implements(
        gocept.registration.interfaces.IConfirmationEmail)

    def __init__(self, registration):
        config = gocept.registration.interfaces.IEmailConfiguration(
            registration)
        self.message = config.confirmation_template % {
            'to': registration.email,
            'from': config.addr_from,
            'link': config.confirmation_url % registration.hash}


@zope.component.adapter(gocept.registration.interfaces.IRegistration,
                        zope.app.container.interfaces.IObjectAddedEvent)
def send_registration_mail(registration, event):
    """Listen for a registration and send a mail to the user, asking for
    confirmation.
    """
    email = gocept.registration.interfaces.IConfirmationEmail(registration)
    config = gocept.registration.interfaces.IEmailConfiguration(registration)
    mailer = zope.component.getUtility(zope.sendmail.interfaces.IMailDelivery)
    mailer.send(config.addr_from, [registration.email], email.message)
