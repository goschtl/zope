##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Generic registry of ids to objects."""

from zope.interface.verify import verifyClass
from zope.app.interfaces.security import IRegisteredObject
from zope.exceptions import ZopeError


class AlreadyRegisteredError(ZopeError, ValueError):
    """An attempt was made to register an object with an already registered id.
    """


class Registry:
    def __init__(self, class_):
        """Instantiate a generic registry.

        class_ is the class of the thing that we're going to instantiate.
        """
        assert verifyClass(IRegisteredObject, class_)
        self._class = class_
        self._clear()

    def register(self, id, title='', description=''):
        """Create a registered object with the given id, title, and description

        Register and return the object.  The empty string will be used if
        either the optional title or description is omitted.  The id must be
        unique.

        If the id is already registered, an AlreadyRegisteredError is raised.
        """
        if id in self._byid:
            raise AlreadyRegisteredError('Id is not unique: %s' % id)
        obj = self._class(id, title, description)
        self._byid[id] = obj
        return obj

    def is_registered(self, id):
        """Return true if an object is registered with the given id.
        Otherwise false is returned.
        """
        return id in self._byid

    def getRegisteredObject(self, id):
        """Return the object registered under the given id.
        """
        return self._byid.get(id)

    def getRegisteredObjects(self):
        """Return all registered objects.
        """
        return self._byid.values()

    def _clear(self):
        # Map ids to instantiated objects
        self._byid = {}
