##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Implementation of `IPrincipalAnnotationUtility`.

$Id$
"""
__docformat__ = 'restructuredtext'

# TODO: register utility as adapter for IAnnotations on utility activation.

from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOBTree
from zope.interface import implements

from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.contained import Contained
from zope.app.location import Location
from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.app.component import queryNextUtility

class PrincipalAnnotationUtility(Persistent, Contained):
    """Stores `IAnnotations` for `IPrinicipals`.

    The utility ID is 'PrincipalAnnotation'.
    """

    implements(IPrincipalAnnotationUtility)

    def __init__(self):
        self.annotations = OOBTree()

    def getAnnotations(self, principal):
        """Return object implementing IAnnotations for the given principal.

        If there is no `IAnnotations` it will be created and then returned.
        """
        return self.getAnnotationsById(principal.id)

    def getAnnotationsById(self, principalId):
        """Return object implementing `IAnnotations` for the given principal.

        If there is no `IAnnotations` it will be created and then returned.
        """

        annotations = self.annotations.get(principalId)
        if annotations is None:
            annotations = Annotations(principalId, store=self.annotations)
            annotations.__parent__ = self
            annotations.__name__ = principalId

        return annotations

    def hasAnnotations(self, principal):
        """Return boolean indicating if given principal has `IAnnotations`."""
        return principal.id in self.annotations


class Annotations(Persistent, Location):
    """Stores annotations."""

    implements(IAnnotations)

    def __init__(self, principalId, store=None):
        self.principalId = principalId
        self.data = PersistentDict() # We don't really expect that many

        # _v_store is used to remember a mapping object that we should
        # be saved in if we ever change
        self._v_store = store

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            # We failed locally: delegate to a higher-level utility.
            utility = queryNextUtility(self, IPrincipalAnnotationUtility)
            if utility is not None:
                annotations = utility.getAnnotationsById(self.principalId)
                return annotations[key]
            raise

    def __setitem__(self, key, value):
        if getattr(self, '_v_store', None) is not None:
            # _v_store is used to remember a mapping object that we should
            # be saved in if we ever change
            self._v_store[self.principalId] = self
            del self._v_store

        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


class AnnotationsForPrincipal(object):
    """Adapter from IPrincipal to `IAnnotations` for a
    `PrincipalAnnotationUtility`.

    Register an *instance* of this class as an adapter.
    """

    def __init__(self, utility):
        self.utility = utility

    def __call__(self, principal):
        return self.utility.getAnnotationsById(principal.id)


#############################################################################
# BBB: 12/20/2004
PrincipalAnnotationService = PrincipalAnnotationUtility
#############################################################################
