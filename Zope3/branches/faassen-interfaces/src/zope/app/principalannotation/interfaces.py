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
"""Service for storing IAnnotations for principals.

$Id: interfaces.py,v 1.1 2004/03/13 18:44:48 srichter Exp $
"""
from zope.interface import Interface


class IPrincipalAnnotationService(Interface):
    """Stores IAnnotations for IPrinicipals."""

    def getAnnotations(principal):
        """Return object implementing IAnnotations for the given IPrinicipal.

        If there is no IAnnotations it will be created and then returned.
        """

    def getAnnotationsById(principalId):
        """Return object implementing IAnnotations for the given prinicipal id.

        If there is no IAnnotations it will be created and then returned.
        """

    def hasAnnotations(principal):
        """Return boolean indicating if given IPrincipal has IAnnotations."""
