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

$Id: interfaces.py,v 1.7 2003/06/05 11:45:03 mgedmin Exp $
"""

from zope.interface import Interface, Attribute

class ISecurityManagementSetup(Interface):
    """Methods to manage the security manager.

    Infrastructure (including tests, etc.) calls these things to
    tweak the security manager.
    """

    def newSecurityManager(user):
        """Install a new SecurityManager, using user.

        Return the old SecurityManager, if any, or None.
        """

    def replaceSecurityManager(old_manager):
        """Replace the SecurityManager with old_manager.

        old_manager must implement ISecurityManager.
        """

    def noSecurityManager():
        """Clear any existing SecurityManager."""

class ISecurityManagement(Interface):
    """Public security management API."""

    def getSecurityManager():
        """Get a SecurityManager (create if needed)."""

    def setSecurityPolicy(aSecurityPolicy):
        """Set the system default security policy.

        This method should only be called by system startup code.  It
        should never, for example, be called during a web request.
        """

class ISecurityProxyFactory(Interface):

    def __call__(object, checker=None):
        """Create a security proxy

        If a checker is given, then use it, otherwise, try to figure
        out a checker.

        If the object is already a security proxy, then it will be
        returned.
        """

# XXX This interface has too much Zope application dependence. This
# needs to be refactored somehow.

class ISecurityManager(Interface):
    """
        A security manager provides methods for checking access and managing
        executable context and policies.
    """

    def getPrincipal():
        """Return the authenticated principal.

        This is equivalent to something like::
        REQUEST['AUTHENTICATED_USER']
        but is a bit cleaner, especially if 'REQUEST' isn't handy.

        An IPrincipal object wrapped in a context of its
        AuthenticationService is returned.
        """

    def checkPermission(permission, object):
        """Return whether security context allows permission on object.

        Arguments:
        permission -- A permission name
        object -- The object being accessed according to the permission
        """

    def pushExecutable(anExecutableObject):
        """
            Push an ExecutableObject onto the manager's stack, and
            activate its custom security policy, if any.
        """

    def popExecutable(anExecutableObject):
        """
            Pop the topmost ExecutableObject from the stack, deactivating
            any custom security policy it might have installed.
        """

    def calledByExecutable():
        """
            Return a boolean indicating whether the current request has
            invoked any IExecutableObjects.

            This can be used to determine if an object was called
            (more or less) directly from a URL, or if it was called by
            through-the-web provided code.
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

    def checkPermission(permission, object, context):
        """Return whether security context allows permission on object.

        Arguments:
        permission -- A permission name
        object -- The object being accessed according to the permission
        context -- A SecurityContext, which provides access to information
            such as the context stack and AUTHENTICATED_USER.
        """


class ISecurityContext(Interface):
    """Capture transient request-specific security information."""

    Attribute('stack',
              'A stack of elements, each either be an ExecutableObject'
              'or a tuple consisting of an ExecutableObject and a'
              'custom SecurityPolicy.'
            )

    Attribute('user',
              'The AUTHENTICATED_USER for the request.'
              )
