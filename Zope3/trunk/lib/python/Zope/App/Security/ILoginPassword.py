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
from Interface import Interface


class ILoginPassword(Interface):
    """A password based login.

    An IAuthenticationService would use this (adapting a request),
    to discover the login/password passed from the user, or to
    indicate that a login is required.
    """
    
    def getLogin():
        """Return login name, or None if no login name found."""

    def getPassword():
        """Return password, or None if no login name found.
        
        If there's a login but no password, return empty string.
        """

    def needLogin(realm):
        """Indicate that a login is needed.

        The realm argument is the name of the principal registry.
        """
