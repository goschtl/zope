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

"""Service for storing IAnnotations for principals."""

from zope.interface import Interface


class IPrincipalAnnotationService(Interface):
    """Stores IAnnotations for IPrinicipals."""

    def getAnnotation(principal):
        """Return object implementing IAnnotations for the givin IPrinicipal.

        If there is no IAnnotations it will be created and then returned.
        """

    def hasAnnotation(principal):
        """Return boolean indicating if given IPrincipal has IAnnotations."""
