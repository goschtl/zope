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
"""A utility for managing registrations."""

import datetime
import gocept.registration.interfaces
import persistent
import sha
import zope.app.container.btree
import zope.interface


class Registration(zope.app.container.contained.Contained,
                   persistent.Persistent):

    zope.interface.implements(gocept.registration.interfaces.IRegistration)

    def __init__(self, hash, email, data):
        self.hash = hash
        self.email = email
        self.data = data


class Registrations(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(gocept.registration.interfaces.IRegistrations)

    def _createHash(self, email, data=None):
        return sha.new(email+datetime.datetime.now().isoformat()).hexdigest()

    def register(self, email, data=None, factory=Registration):
        """Create a new registration for the given email address and data."""
        hash = self._createHash(email, data)
        self[hash] = registration = factory(hash, email, data)
        return registration

    def confirm(self, hash):
        """Confirm the registration identified by the hash."""
        registration = self[hash]

        event = gocept.registration.interfaces.RegistrationConfirmedEvent(
            registration)
        zope.event.notify(event)

        del self[hash]
