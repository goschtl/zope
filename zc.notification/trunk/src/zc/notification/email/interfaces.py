##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for the email support for the notification utility.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

import zc.notification.interfaces

from zc.notification.i18n import _


class IEmailNotifier(zc.notification.interfaces.INotifier):
    """Notifier that sends email.

    """

    fromAddress = zope.schema.ASCIILine(
        title=_(u"From address"),
        description=_(u"Email address used for the From: header."),
        required=True,
        )

    fromName = zope.schema.ASCIILine(
        title=_(u"From name"),
        description=_(u"Name to use in the From: header."),
        required=False,
        )


class IEmailLookupUtility(zope.interface.Interface):
    """Utility that can retrieve an email address for a principal.

    """

    def getAddress(principal_id, annotations):
        """Return an email address as a string, or None.

        `principal_id` is a principal id.

        `annotations` is the principal annotations corresponding to
        `principal_id`.

        """


class IEmailView(zope.interface.Interface):
    """View that generates an email.

    Email views are adaptations of a notification and a principal.
    The principal is the recipient of the email, not necessarily the
    principal who caused the notification to be sent.

    """

    def render():
        """Return the rendered email.

        The generated email should include the RFC-2822 headers
        (except the To: and From: headers), and the blank line that
        follows them, and the email payload.

        The return value should be an 8-bit string; it will not be
        further encoded before being passed to the `IMailDelivery`
        utility.

        """
