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

# XXX This interface has too muct Zope application dependence. This
# needs to be refactored somehow.

class ISecurityManager( Interface ):
    """
        A security manager provides methods for checking access and managing
        executable context and policies.
    """

    def getPrincipal():
        """
            Return the authenticated principal. 

            This is equivalent to something like::

            REQUEST['AUTHENTICATED_USER']

            but is a bit cleaner, especially if 'REQUEST' isn't handy.
        """

    def checkPermission( permission, object ):
        """
            Check whether the security context allows the given
            permission on the given object. Return a boolean value.

            Arguments:

            permission -- A permission name

            object -- The object being accessed according to the permission
        """

    def pushExecutable( anExecutableObject ):
        """
            Push an ExecutableObject onto the manager's stack, and
            activate its custom security policy, if any.
        """

    def popExecutable( anExecutableObject ):
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
