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
"""
$Id: IUser.py,v 1.1 2002/07/13 16:52:57 srichter Exp $
"""
from Interface import Interface
from Zope.App.Security.IPrincipal import IPrincipal

class IReadUser(IPrincipal):
    """Read interface for a User."""

    def getLogin():
        """Get the login for the user."""

    def validate(pw):
        """Seee whether the password is valid."""


class IWriteUser(Interface):
    """Write interface for a User."""

    def setTitle(title):
        """Set title of User."""

    def setDescription(description):
        """Set description of User."""

    def setLogin(login):
        """Set login of User."""

    def setPassword(password):
        """Set password of User."""


class IUser(IReadUser, IWriteUser):
    """A user object for the Local Authentication Service."""
