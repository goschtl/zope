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
$Id: auth.py,v 1.5 2003/02/11 15:59:51 sidnei Exp $
"""
from zope.interface import Interface
from zope.app.interfaces.security import IPrincipal
from zope.app.interfaces.annotation import IAttributeAnnotatable

class IReadUser(IPrincipal):
    """Read interface for a User."""

    def getLogin():
        """Get the login for the user."""

    def validate(pw):
        """See whether the password is valid."""


class IWriteUser(Interface):
    """Write interface for a User."""

    def setTitle(title):
        """Set title of User."""

    def setDescription(description):
        """Set description of User."""

    def setLogin(login):
        """Set login of User."""

    def setRoles(roles):
        """Set roles of User.

        Roles should be a sequence of role ids.
        """

    def setPassword(password):
        """Set password of User."""


class IUser(IReadUser, IWriteUser):
    """An user object for the Local Authentication Service."""

class IAnnotatableUser(IUser, IAttributeAnnotatable):
    """An annotatable user object for the Local Authentication Service."""
