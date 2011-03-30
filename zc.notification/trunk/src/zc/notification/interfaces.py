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
"""Interfaces for the notification utility.

"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from zc.notification.i18n import _


class INotificationUtility(zope.interface.Interface):
    """Notification utility.

    """

    def notify(notification, context=None):
        """Process a notification.

        `notification` must implement `INotification`.

        """


class INotification(zope.interface.Interface):
    """Individual notification.

    """

    name = zope.schema.TextLine(
        title=_("Name"),
        description=_(u"Name of the notification"),
        required=True,
        )

    # This should be a zope.i18nmessageid.Message.
    summary = zope.schema.TextLine(
        title=_("Summary"),
        description=_("Optional one-line message summary."),
        required=False)

    # This should be a zope.i18nmessageid.Message.
    message = zope.interface.Attribute(
        "Message associated with this notification."
        )

    mapping = zope.interface.Attribute(
        """A dictionary of name: i18nmessageid.Message to be translated and 
        then included in message translation, or None""")

    timestamp = zope.schema.Datetime(
        title=_(u"Time"),
        description=_(u"Time that the notification was generated."
                      u" This is given in UTC with the tzinfo set."),
        required=True,
        )

    def applicablePrincipals(principal_ids):
        """Return the set of principal ids this notification should be sent to.

        `principal_ids` is a set of principal ids.

        """


# User interfaces will want some way of describing notifications; each
# should be described using an `INotificationDefinition`.  These can
# be utilities looked up by name, where the name matches that of the
# notifications.

class INotificationDefinition(zope.interface.Interface):
    """Information about a type of notification.

    This should be used to generate user-interfaces, which may include
    representations of the individual notifications.

    """

    name = zope.schema.TextLine(
        title=_("Name"),
        description=_(u"Name of the notification"),
        required=True,
        )

    # This should be a zope.i18nmessageid.Message.
    title = zope.interface.Attribute(
        "Short human-consumable name of the notification."
        )

    # This should be a zope.i18nmessageid.Message.
    description = zope.interface.Attribute(
        "Human-consumable description of the notification."
        " This should include what triggers the notification."
        )


# The following interfaces are defined for use by the reference
# implementation; these may not be used by alternate implementations.

class INotifier(zope.interface.Interface):
    """Object responsible for sending a notification to principals.

    """

    def send(notification, principal_id, annotations, context):
        """Send one notification to one principal.

        `notification` must implement `INotification`.

        `principal_id` is a principal id.

        `annotations` is the annotations object for the principal.

        `context` is a context in which utilities and other components
        should be looked up, and may be None (indicating the default
        look up).

        """


class INotificationUtilityConfiguration(zope.interface.Interface):
    """Configuration interface for the notification utility.

    """

    def setNotifierMethod(principal_id, method, context=None):
        """Set the preferred notifier method for `principal_id`.

        """

    def getNotifierMethod(principal_id, context=None):
        """Return the preferred notifier method for `principal_id`.

        """

    def setRegistrations(principal_id, names):
        """Replace the existing registrations for `principal_id`.

        Existing registrations are removed if not included in `names`,
        and all registrations from `names` are added if not already
        present.

        """

    def getRegistrations(principal_id):
        """Return the current set of registrations for `principal_id`.

        """

    def getNotificationSubscriptions(notification_name):
        """Return the current set of subscribers for `notification_name`.

        """

class INotificationSubscriptions(zope.interface.Interface):

    notifications = zope.schema.Set(
        title=_(u'Notifications'),
        description=_(u'Available Notifications'),
        required=True,
        value_type=zope.schema.Choice(
            vocabulary='zc.notification.notifications'))


class IPreferredNotifierMethod(zope.interface.Interface):

    method = zope.schema.Choice(
        title=_(u'Notifier'),
        description=_(u'Preferred means of being notified'),
        vocabulary='zc.notification.notifiers')
