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

class ISecurityManagementSetup( Interface ):
    """
        Infrastructure (including tests, etc.) calls these things to
        tweak the security manager.
    """
    def newSecurityManager( user ):
        """
            Install a new SecurityManager, using user.  Return the
            old SecurityManager, if any, or None.
        """

    def replaceSecurityManager( old_manager ):
        """
            Replace the SecurityManager with 'old_manager', which
            must implement ISecurityManager.
        """

    def noSecurityManager():
        """
            Clear any existing SecurityManager.
        """

class ISecurityManagement( Interface ):
    """
        "Public" SM API.
    """
    def getSecurityManager():
        """
            Get a SecurityManager (create if needed).
        """

    def setSecurityPolicy( aSecurityPolicy ):
        """
            Set the system default security policy. 

            This method should only be called by system startup code.
            It should never, for example, be called during a web request.
        """
