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
"""User and Authentication Service Interfaces.

$Id: auth.py,v 1.8 2004/03/08 12:07:03 srichter Exp $
"""
from zope.interface import Interface
from zope.app.security.interfaces import IPrincipal
from zope.app.interfaces.annotation import IAttributeAnnotatable

class IReadUser(IPrincipal):
    """Read interface for a User."""

    def getLogin():
        """Get the login for the user."""

    def validate(pw):
        """Confirm whether pw is the password of the user."""


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
    """An user object for the Local Authentication Service."""

class IAnnotatableUser(IUser, IAttributeAnnotatable):
    """An annotatable user object for the Local Authentication Service."""
