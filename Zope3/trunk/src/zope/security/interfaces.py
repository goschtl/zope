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
"""Interfaces for security machinery.

$Id$
"""
from zope.interface import Interface, Attribute


class ISecurityManagement(Interface):
    """Public security management API."""

    def getSecurityPolicy():
        """Get the system default security policy."""

    def setSecurityPolicy(aSecurityPolicy):
        """Set the system default security policy.

        This method should only be called by system startup code.  It
        should never, for example, be called during a web request.
        """


class ISecurityChecking(Interface):
    """Public security API."""

    def checkPermission(permission, object, interaction=None):
        """Return whether security policy allows permission on object.

        Arguments:
        permission -- A permission name
        object -- The object being accessed according to the permission
        interaction -- An interaction, which provides access to information
            such as authenticated principals.  If it is None, the current
            interaction is used.
        """


class ISecurityProxyFactory(Interface):

    def __call__(object, checker=None):
        """Create a security proxy

        If a checker is given, then use it, otherwise, try to figure
        out a checker.

        If the object is already a security proxy, then it will be
        returned.
        """


class IChecker(Interface):
    """Security-proxy plugin objects that implement low-level checks

    The checker is responsible for creating proxies for
    operation return values, via the proxy method.

    There are check_getattr() and check_setattr() methods for checking
    getattr and setattr, and a check() method for all other operations.

    The check methods may raise errors.  They return no value.

    Example (for __getitem__):

           checker.check(ob, \"__getitem__\")
           return checker.proxy(ob[key])
    """

    def check_getattr(ob, name):
        """Check whether attribute access is allowed."""

    def check_setattr(ob, name):
        """Check whether attribute assignment is allowed."""

    def check(ob, operation):
        """Check whether operation is allowed.

        The operation name is the Python special method name,
        e.g. "__getitem__".
        """

    def proxy(value):
        """Return a security proxy for the value."""


class INameBasedChecker(IChecker):
    """Security checker that uses permissions to check attribute access."""

    def permission_id(name):
        """Return the permission used to check attribute access on name.

        This permission is used by both check and check_getattr.
        """

    def setattr_permission_id(name):
        """Return the permission used to check attribute assignment on name.

        This permission is used by check_setattr.
        """


class ISecurityPolicy(Interface):

    def createInteraction(participation=None):
        """Creates a new interaction for a given request.

        If participation is not None, it is added to the new interaction.

        XXX perhaps this should be a separate interface IInteractionFactory,
            and the factory registered by calling
            ISecurityManagement.global setInteractionFactory(factory).
        """

    def checkPermission(permission, object, interaction):
        """Return whether security context allows permission on object.

        Arguments:
        permission -- A permission name
        object -- The object being accessed according to the permission
        interaction -- An interaction, which provides access to information
            such as authenticated principals.
        """


class IInteraction(Interface):
    """A representation of an interaction between some actors and the system.
    """

    participations = Attribute("""An iterable of participations.""")

    def add(participation):
        """Add a participation."""

    def remove(participation):
        """Remove a participation."""


class IParticipation(Interface):

    interaction = Attribute("The interaction")
    principal = Attribute("The authenticated principal")


class IInteractionManagement(Interface):
    """Interaction management API.

    Every thread has at most one active interaction at a time.
    """

    def newInteraction(participation=None):
        """Start a new interaction.

        If participation is not None, it is added to the new interaction.

        Raises an error if the calling thread already has an interaction.
        """

    def queryInteraction():
        """Return the current interaction.

        Returns None if there is no interaction.
        """

    def endInteraction():
        """End the current interaction.

        Does nothing if there is no interaction.
        """

