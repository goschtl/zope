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
"""Default 'ISecurityManagement' and 'IInteractionManagement' implementation

$Id: management.py,v 1.5 2004/02/20 20:42:12 srichter Exp $
"""
# Special system user that has all permissions
# zope.security.manager needs it
system_user = object()

from zope.interface import moduleProvides
from zope.security.interfaces import ISecurityManagement
from zope.security.interfaces import ISecurityManagementSetup
from zope.security.interfaces import IInteractionManagement
from zope.security.manager import SecurityManager
from zope.security.manager import setSecurityPolicy as _setSecurityPolicy
from zope.security.manager import getSecurityPolicy as _getSecurityPolicy
from zope.security.context import SecurityContext
from zope.testing.cleanup import addCleanUp
from zope.thread import thread_globals

moduleProvides(ISecurityManagement, ISecurityManagementSetup,
               IInteractionManagement)

try:
    import thread
except:
    get_ident = lambda: 0
else:
    get_ident = thread.get_ident

_managers = {}

from zope.testing.cleanup import addCleanUp
addCleanUp(_managers.clear)

#
#   ISecurityManagementSetup implementation
#
def newSecurityManager(user):
    """Install a new SecurityManager, using user.

    Return the old SecurityManager, if any, or None.
    """
    return replaceSecurityManager(SecurityManager(SecurityContext(user)))

def replaceSecurityManager(old_manager):
    """Replace the SecurityManager with 'old_manager', which must
    implement ISecurityManager.
    """

    thread_id = get_ident()
    old = _managers.get(thread_id, None)
    _managers[thread_id] = old_manager
    return old

def noSecurityManager():
    """Clear any existing SecurityManager."""
    try:
        del _managers[get_ident()]
    except KeyError:
        pass

#
#   ISecurityManagement implementation
#
def getSecurityManager():
    """Get a SecurityManager (create if needed)."""
    thread_id = get_ident()
    manager = _managers.get(thread_id, None)

    if manager is None:
        newSecurityManager(None)
        manager = _managers.get(thread_id, None)

    return manager

def getSecurityPolicy():
    """Get the system default security policy."""
    return _getSecurityPolicy()

def setSecurityPolicy(aSecurityPolicy):
    """Set the system default security policy, and return the previous
    value.

    This method should only be called by system startup code.
    It should never, for example, be called during a web request.
    """
    return _setSecurityPolicy(aSecurityPolicy)


#
#   IInteractionManagement implementation
#

def getInteraction(_thread=None):
    """Get the current interaction."""
    return thread_globals(_thread).interaction

def newInteraction(participation=None, _thread=None, _policy=None):
    """Start a new interaction."""
    if getInteraction(_thread) is not None:
        stack = getInteraction(_thread)._newInteraction_called_from
        raise AssertionError("newInteraction called"
                             " while another interaction is active:\n%s"
                             % "".join(traceback.format_list(stack)))
    interaction = _defaultPolicy.createInteraction(participation)
    interaction._newInteraction_called_from = traceback.extract_stack()
    thread_globals(_thread).interaction = interaction

def endInteraction(_thread=None):
    """End the current interaction."""
    if getInteraction(_thread=_thread) is None:
        raise AssertionError("endInteraction called"
                             " without an active interaction")
    thread_globals(_thread).interaction = None


def _cleanUp():
    thread_globals().interaction = None

addCleanUp(_cleanUp)


