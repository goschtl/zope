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
""" Default ISecurityManagement implementation """

system_user = object() # Special system user that has all permissions


from zope.security.interfaces import ISecurityManagement, ISecurityManagementSetup
from zope.security.securitymanager import SecurityManager
from zope.security.securitymanager import setSecurityPolicy as _setSecurityPolicy
from zope.security.securitycontext import SecurityContext

__implements__ = ( ISecurityManagement, ISecurityManagementSetup )

try:
    import thread
except:
    get_ident=lambda: 0
else:
    get_ident=thread.get_ident

_managers={}

from zope.testing.cleanup import addCleanUp
addCleanUp(_managers.clear)


#
#   ISecurityManagementSetup implementation
#
def newSecurityManager( user ):
    """
        Install a new SecurityManager, using user.  Return the
        old SecurityManager, if any, or None.
    """
    return replaceSecurityManager( SecurityManager( SecurityContext( user ) ) )

def replaceSecurityManager( old_manager ):
    """
        Replace the SecurityManager with 'old_manager', which
        must implement ISecurityManager.
    """
    thread_id = get_ident()
    old = _managers.get( thread_id, None )
    _managers[ thread_id ] = old_manager
    return old

def noSecurityManager():
    """
        Clear any existing SecurityManager.
    """
    try:
        del _managers[ get_ident() ]
    except KeyError:
        pass

#
#   ISecurityManagement implementation
#
def getSecurityManager():
    """
        Get a SecurityManager (create if needed).
    """
    thread_id = get_ident()
    manager=_managers.get( thread_id, None )

    if manager is None:
        newSecurityManager( None )
        manager=_managers.get( thread_id, None )

    return manager

def setSecurityPolicy( aSecurityPolicy ):
    """
        Set the system default security policy, and return the previous
        value.

        This method should only be called by system startup code.
        It should never, for example, be called during a web request.
    """
    return _setSecurityPolicy( aSecurityPolicy )
