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
"""Default ISecurityManager implementation

$Id: manager.py,v 1.4 2003/06/02 14:34:49 stevea Exp $
"""
from zope.interface import implements
from zope.security.simplepolicies import ParanoidSecurityPolicy

MAX_STACK_SIZE = 100

_defaultPolicy = ParanoidSecurityPolicy()

def _clear():
    global _defaultPolicy
    _defaultPolicy = ParanoidSecurityPolicy()

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)


def setSecurityPolicy(aSecurityPolicy):
    """Set the system default security policy.

    This method should only be caused by system startup code. It should never,
    for example, be called during a web request.
    """
    global _defaultPolicy

    last, _defaultPolicy = _defaultPolicy, aSecurityPolicy

    return last

from zope.security.interfaces import ISecurityManager

class SecurityManager:
    """A security manager provides methods for checking access and managing
    executable context and policies.
    """
    implements(ISecurityManager)

    def __init__(self, context):
        self._context = context
        self._policy = None

    def _getPolicy(self):
        """Find current policy, or default.
        """
        policy = self._policy
        if policy is None:
            policy = _defaultPolicy
        return policy

    #
    #   ISecurityManager implementation
    #
    def getPrincipal(self):
        """Return the authenticated user.

       This is equivalent to something like::

         REQUEST['AUTHENTICATED_USER']

        but is a bit cleaner, especially if 'REQUEST' isn't handy.
        """
        return self._context.user

    def checkPermission(self, permission, object):
        """Check whether the security context allows the given
        permission on the given object. Return a boolean value.

        Arguments:

            permission -- A permission name

            object -- The object being accessed according to the permission
        """
        return self._getPolicy().checkPermission(permission, object,
                                                 self._context)

    def pushExecutable(self, anExecutableObject):
        """Push an ExecutableObject onto the manager's stack, and
        activate its custom security policy, if any.
        """
        stack = self._context.stack

        if len(stack) >= MAX_STACK_SIZE:
            raise SystemError, 'Excessive recursion'

        stack.append(anExecutableObject)
        p = getattr(anExecutableObject, '_customSecurityPolicy', None)

        if p is not None:
            p = p()

        self._policy = p

    def popExecutable(self, anExecutableObject):
        """Pop the topmost ExecutableObject from the stack, deactivating
        any custom security policy it might have installed.
        """
        stack = self._context.stack

        if not stack:
            return

        top = stack[-1]

        if top is anExecutableObject:
            del stack[-1]
        else:
            indexes = range(len(stack))
            indexes.reverse()
            for i in indexes:
                top = stack[i]
                if top is anExecutableObject:
                    del stack[i:]
                    break
            else:
                return

        if stack:
            top = stack[-1]
            p = getattr(top, '_customSecurityPolicy', None)

            if p is not None:
                p = p()
            self._policy = p
        else:
            self._policy = None

    def calledByExecutable(self):
        """Return a boolean indicating whether the current request has
        invoked any IExecutableObjects.

        This can be used to determine if an object was called (more or less)
        directly from a URL, or if it was called by through-the-web provided
        code.
        """
        return len(self._context.stack)
