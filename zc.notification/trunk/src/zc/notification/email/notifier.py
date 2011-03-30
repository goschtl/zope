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
"""Basic utility to convert notifications into email.

"""
__docformat__ = "reStructuredText"

import logging

import persistent

import zope.component

import zope.app.container.interfaces
import zope.app.container.contained
import zope.app.security.interfaces
import zope.sendmail.interfaces

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

    def send(self, notification, principal_id, annotations, context):
        address = self.email_lookup(context).getAddress(
            principal_id, annotations)
        if address:
            # send some email
            principal = zope.component.getUtility(
                zope.app.security.interfaces.IAuthentication,
                context=context).getPrincipal(principal_id)
            view = zope.component.getMultiAdapter(
                (notification, principal),
                zc.notification.email.interfaces.IEmailView,
                context=context)
            if self.fromName:
                response = ("From: %s <%s>\r\n"
                            % (self.fromName, self.fromAddress))
            else:
                response = "From: %s\r\n" % self.fromAddress
            response += "To: %s\r\n" % address
            response += view.render()
            self.mailer(context).send(self.fromAddress, [address], response)
        else:
            _log.info("No email address for principal id %r." % principal_id)

    _v_email_lookup_utility = None
    _v_mailer = None
    _v_context = None

    def email_lookup(self, context):
        if (self._v_email_lookup_utility is None or
            context is not self._v_context):
            utility = zope.component.getUtility(
                zc.notification.email.interfaces.IEmailLookupUtility,
                context=context)
            self._v_email_lookup_utility = utility
            self._v_context = context
        return self._v_email_lookup_utility

    def mailer(self, context):
        if self._v_mailer is None or context is not self._v_context:
            utility = zope.component.getUtility(
                zope.sendmail.interfaces.IMailDelivery,
                context=context)
            self._v_mailer = utility
            self._v_context = context
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
