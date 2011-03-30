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
"""Simple reference implementation of the notification tools.

"""
__docformat__ = "reStructuredText"

import datetime

import BTrees.OOBTree
import pytz
import persistent

import zope.component
import zope.interface
import zope.schema.vocabulary
import zope.schema.interfaces
import zope.app.container.interfaces
import zope.app.container.contained

from zope.annotation.interfaces import IAnnotations

import zc.notification.interfaces


def getNotificationNames(context):
    N = zope.component.getUtilitiesFor(
        zc.notification.interfaces.INotificationDefinition,
        context=context)
    return zope.schema.vocabulary.SimpleVocabulary.fromValues(
        [name for (name, utility) in N])
zope.interface.directlyProvides(
    getNotificationNames, zope.schema.interfaces.IVocabularyFactory)

def getNotifierMethods(context):
    N = zope.component.getUtilitiesFor(
        zc.notification.interfaces.INotifier,
        context=context)
    return zope.schema.vocabulary.SimpleVocabulary.fromValues(
        [name for (name, utility) in N])
zope.interface.directlyProvides(
    getNotifierMethods, zope.schema.interfaces.IVocabularyFactory)


class Notification(object):
    """Really basic notification object.

    """

    zope.interface.implements(
        zc.notification.interfaces.INotification)

    name = message = mapping= event = timestamp = summary = None

    def __init__(self, name, message, mapping=None, summary=None):
        self.name = name
        self.message = message
        self.mapping = mapping
        self.summary = summary
        self.timestamp = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

    def applicablePrincipals(self, principal_ids):
        """Please(!) override in subclass!

        Really.  This is very noisy.

        """

        return principal_ids

class PrincipalNotification(Notification):

    def __init__(self,
                 name, message, principal_ids, mapping=None, summary=None):
        super(PrincipalNotification, self).__init__(
            name, message, mapping, summary)
        self.principal_ids = frozenset(principal_ids)

    def applicablePrincipals(self, principal_ids):
        return self.principal_ids.intersection(principal_ids)

class GroupAwarePrincipalNotification(PrincipalNotification):

    def __init__(self,
                 name, message, principal_ids, mapping=None, summary=None,
                 exclude_ids=frozenset(), context=None):
        super(GroupAwarePrincipalNotification, self).__init__(
            name, message, principal_ids, mapping, summary)
        self.principals = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication,
            context=context)
        self.group_ids = frozenset(
            pid for pid in self.principal_ids if
            zope.security.interfaces.IGroup.providedBy(
                self.principals.getPrincipal(pid)))
        self.exclude_ids = exclude_ids

    def applicablePrincipals(self, principal_ids):
        res = set()
        for pid in principal_ids:
            if pid in self.exclude_ids:
                continue
            if pid not in self.principal_ids:
                if not self.group_ids:
                    continue
                # go through all groups of pid and see if they are in
                # performers.  if not, continue
                seen = set()
                p = self.principals.getPrincipal(pid)
                groups = getattr(p, 'groups', ())
                if groups:
                    stack = [iter(groups)]
                    while stack:
                        try:
                            gid = stack[-1].next()
                        except StopIteration:
                            stack.pop()
                        else:
                            if gid not in seen:
                                seen.add(gid)
                                if gid in self.group_ids:
                                    break
                                p = self.principals.getPrincipal(gid)
                                groups = getattr(p, 'groups', ())
                                if groups:
                                    stack.append(iter(groups))
                    else:
                        continue
                else:
                    continue
            res.add(pid)
        return res


PREFERRED_METHOD_ANNOTATION_KEY = "zc.notification.preferred_method"


class NotificationUtility(zope.app.container.contained.Contained,
                          persistent.Persistent):
    """Utility implementation.

    """

    zope.interface.implements(
        zope.app.container.interfaces.IContained,
        zc.notification.interfaces.INotificationUtility,
        zc.notification.interfaces.INotificationUtilityConfiguration)

    def __init__(self):
        # notification name --> Set([principal_ids])
        self._notifications = BTrees.OOBTree.OOBTree()
        # principal_id --> Set([notification names])
        self._registrations = BTrees.OOBTree.OOBTree()

    def get_annotations(self, principal_id, context=None):
        principals = zope.component.getUtility(
            zope.app.security.interfaces.IAuthentication,
            context=context)
        principal = principals.getPrincipal(principal_id)
        return zope.component.getMultiAdapter((principal, context),
                                              IAnnotations)

    def setNotifierMethod(self, principal_id, method, context=None):
        annotations = self.get_annotations(principal_id, context)
        annotations[PREFERRED_METHOD_ANNOTATION_KEY] = method

    def getNotifierMethod(self, principal_id, context=None):
        annotations = self.get_annotations(principal_id, context)
        return annotations.get(PREFERRED_METHOD_ANNOTATION_KEY, "")

    def setRegistrations(self, principal_id, names):
        names = set(names)
        current = self.getRegistrations(principal_id)
        added = names - current
        removed = current - names
        notifications = self._notifications

        # We would use .setdefault() here, but Zope 3.1 doesn't have that.

        for name in added:
            principals = notifications.get(name)
            if principals is None:
                principals = set()
            principals.add(principal_id)
            notifications[name] = principals

        for name in removed:
            principals = notifications.get(name)
            if principals is None:
                principals = set()
            principals.discard(principal_id)
            notifications[name] = principals

        self._registrations[principal_id] = names

    def getRegistrations(self, principal_id):
        return self._registrations.get(principal_id, set())

    def getNotificationSubscriptions(self, notification_name):
        return self._notifications.get(notification_name, set())

    def notify(self, notification, context=None):
        ids = notification.applicablePrincipals(
            set(self._notifications.get(notification.name, ())))

        for id in ids:
            annotations = self.get_annotations(id, context)
            method = annotations.get(PREFERRED_METHOD_ANNOTATION_KEY, "")
            notifier = None
            if method:
                notifier = zope.component.queryUtility(
                    zc.notification.interfaces.INotifier,
                    name=method,
                    context=context)
            if notifier is None:
                notifier = zope.component.getUtility(
                    zc.notification.interfaces.INotifier,
                    context=context)
            notifier.send(
                notification, id, annotations, context)
