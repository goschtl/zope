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

"""Implementation of IPrincipalAnnotationService."""

# TODO: register service as adapter for IAnnotations on service activation
# this depends on existence of LocalAdapterService, so once that's done
# implement this.

# Zope3 imports
from persistence import Persistent
from zodb.btrees.OOBTree import OOBTree
from zope.app.component.nextservice import getNextService
from zope.proxy.context import ContextMethod
from zope.proxy.context import ContextWrapper
from zope.app.interfaces.annotation import IAnnotations

# Sibling imports
from zope.app.interfaces.services.principalannotation import IPrincipalAnnotationService
from zope.app.interfaces.services.service import ISimpleService

class PrincipalAnnotationService(Persistent):
    """Stores IAnnotations for IPrinicipals.

    The service ID is 'PrincipalAnnotation'.
    """

    __implements__ = (IPrincipalAnnotationService, Persistent.__implements__,
                      ISimpleService)

    def __init__(self):
        self.annotations = OOBTree()


    # implementation of IPrincipalAnnotationService

    def getAnnotation(self, principalId):
        """Return object implementing IAnnotations for the givin principal.

        If there is no IAnnotations it will be created and then returned.
        """
        if not self.annotations.has_key(principalId):
            self.annotations[principalId] = Annotations(principalId)
        return ContextWrapper(self.annotations[principalId], self, name=principalId)

    getAnnotation = ContextMethod(getAnnotation)

    def hasAnnotation(self, principalId):
        """Return boolean indicating if given principal has IAnnotations."""
        return self.annotations.has_key(principalId)


class Annotations(Persistent):
    """Stores annotations."""

    __implements__ = IAnnotations, Persistent.__implements__

    def __init__(self, principalId):
        self.principalId = principalId
        self.data = OOBTree()

    def __getitem__(wrapped_self, key):
        try:
            return wrapped_self.data[key]
        except KeyError:
            # We failed locally: delegate to a higher-level service.
            service = getNextService(wrapped_self, 'PrincipalAnnotation')
            if service:
                return service.getAnnotation(wrapped_self.principalId)[key]
            raise

    __getitem__ = ContextMethod(__getitem__)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def get(self, key, default=None):
        try:
            return self.data[key]
        except KeyError:
            return default


class AnnotationsForPrincipal(object):
    """Adapter from IPrincipal to IAnnotations for a PrincipalAnnotationService.

    Register an *instance* of this class as an adapter.
    """

    def __init__(self, service):
        self.service = service

    def __call__(self, principal):
        return self.service.getAnnotation(principal.getId())
