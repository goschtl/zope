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

class ISecurityPolicy( Interface ):

    def checkPermission( permission
                       , object
                       , context
                       ):
        """
            Check whether the security context allows the given permission on
            the given object, returning a boolean value.

            Arguments:

            permission -- A permission name

            object -- The object being accessed according to the permission

            context -- A SecurityContext, which provides access to information
            shuch as the context stack and AUTHENTICATED_USER.
        """
