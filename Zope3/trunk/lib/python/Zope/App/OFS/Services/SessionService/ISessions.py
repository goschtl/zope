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

"""Interfaces for session service."""

from Interface import Interface


class ISessionService(Interface):
    """Manages sessions - fake state over multiple browser requests."""

    def getSessionId(browserRequest):
        """Return sessionId for the given request.

        If the request doesn't have an attached sessionId a new one will
        be generated.
        
        This will do whatever is possible to do the HTTP request to ensure
        the session id will be preserved. Depending on the specific
        method, further action might be necessary on the part of the user.
        See the documentation for the specific implementation and its
        interfaces.
        """

    def invalidate(sessionId):
        """Destroy all attached data and invalidate the session."""
    
    def getDataManager(name):
        """Get the ISessionDataManager for given name.

        Raises KeyError if name is unknown.
        """


class IConfigureSessionService(Interface):
    """Configuration for ISessionService."""
    
    def registerDataManager(name, dataManager):
        """Register ISessionDataManager under given name.

        Raises ValueError if a data manager with that name already
        """

    def unregisterDataManager(name):
        """Remove ISessionDataManager."""


class ISessionDataManager(Interface):
    """Stores data objects for sessions.

    In general, a data object will be stored for each sessionId requested from
    the ISessionDataManager.
    
    Sub-interfaces should specify the interface(s) implemented by the data
    objects.
    """
    
    def getDataObject(sessionId):
        """Returns data attached to session.

        Should create new object if this is a new session.
        """

    def deleteData(sessionId):
        """Delete data attached to session."""
