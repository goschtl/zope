##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Registration Stack

$Id: registrationstack.py,v 1.1 2004/03/13 18:01:18 srichter Exp $
"""
from zope.app.registration.registration import RegistrationStatusProperty
from zope.app.container.contained import Contained

__metaclass__ = type

class TestingRegistration(Contained):
    status = RegistrationStatusProperty()

    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == getattr(other, 'id', 0)

class TestingRegistrationStack:

    class_ = TestingRegistration

    def __init__(self, *args):
        self._data = args

    def register(self, registration):
        cid = registration.id

        if self._data:
            if cid in self._data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            self._data = (None, )

        self._data += (cid, )

    def unregister(self, registration):
        cid = registration.id

        data = self._data
        if data:
            if data[0] == cid:
                # It's active, we need to switch in None
                self._data = (None, ) + data[1:]
            else:
                self._data = tuple([item for item in data if item != cid])

    def registered(self, registration):
        cid = registration.id
        return cid in self._data

    def activate(self, registration):
        if registration is None:
            self._data = (None,) + filter(None, self._data)
            if self._data[-1] is None:
                self._data = self._data[:-1]
            return
        cid = registration.id
        if self._data[0] == cid:
            return # already active

        if self._data[0] is None:
            # Remove leading None marker
            self._data = self._data[1:]

        self._data = (cid, ) + tuple(
            [item for item in self._data if item != cid]
            )

    def deactivate(self, registration):
        cid = registration.id
        if self._data[0] != cid:
            return # already inactive

        # Just stick None on the front
        self._data = (None, ) + self._data

    def active(self):
        if self._data:
            return self.class_(self._data[0])

        return None

    def __nonzero__(self):
        return bool(self._data)

    def info(self):
        result = [{'id': path,
                   'active': False,
                   'registration': self.class_(path),
                   }
                  for path in self._data
                  ]

        if result:
            if result[0]['registration'] is None:
                del result[0]
            else:
                result[0]['active'] = True

        return result
