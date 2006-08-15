##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
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
"""Basic utility to convert notifications into email.

"""
__docformat__ = "reStructuredText"

import logging

import persistent

import zope.component

import zope.app.container.interfaces
import zope.app.container.contained
import zope.sendmail.interfaces

from zope.app import zapi

import zc.notification.email.interfaces


_log = logging.getLogger(__name__)


class EmailNotifier(zope.app.container.contained.Contained,
                    persistent.Persistent):
    """Send emails for notifications.

    """

    zope.interface.implements(
        zope.app.container.interfaces.IContained,
        zc.notification.email.interfaces.IEmailNotifier)

    fromAddress = None
    fromName = None

    def send(self, notification, principal_id, annotations):
        address = self.email_lookup.getAddress(principal_id, annotations)
        if address:
            # send some email
            principal = zapi.principals().getPrincipal(principal_id)
            view = zope.component.getMultiAdapter(
                (notification, principal),
                zc.notification.email.interfaces.IEmailView)
            if self.fromName:
                response = ("From: %s <%s>\r\n"
                            % (self.fromName, self.fromAddress))
            else:
                response = "From: %s\r\n" % self.fromAddress
            response += "To: %s\r\n" % address
            response += view.render()
            self.mailer.send(self.fromAddress, [address], response)
        else:
            _log.info("No email address for principal id %r." % principal_id)

    _v_email_lookup_utility = None
    _v_mailer = None

    @property
    def email_lookup(self):
        if self._v_email_lookup_utility is None:
            utility = zope.component.getUtility(
                zc.notification.email.interfaces.IEmailLookupUtility)
            self._v_email_lookup_utility = utility
        return self._v_email_lookup_utility

    @property
    def mailer(self):
        if self._v_mailer is None:
            utility = zope.component.getUtility(
                zope.sendmail.interfaces.IMailDelivery)
            self._v_mailer = utility
        return self._v_mailer


EMAIL_ADDRESS_ANNOTATION_KEY = "zc.notification.email.email_address"

class EmailLookupUtility(object):
    """Look up email address for principals.

    The email address is stored as a principal annotation.

    """
    zope.interface.implements(
        zc.notification.email.interfaces.IEmailLookupUtility)

    def getAddress(self, principal_id, annotations):
        return annotations.get(EMAIL_ADDRESS_ANNOTATION_KEY)
