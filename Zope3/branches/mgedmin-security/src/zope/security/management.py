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

import traceback

from zope.interface import moduleProvides
from zope.security.interfaces import ISecurityManagement
from zope.security.interfaces import IInteractionManagement
from zope.security.manager import setSecurityPolicy as _setSecurityPolicy
from zope.security.manager import getSecurityPolicy as _getSecurityPolicy
from zope.testing.cleanup import addCleanUp
from zope.thread import thread_globals

moduleProvides(ISecurityManagement, IInteractionManagement)


#
#   ISecurityManagement implementation
#

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
    interaction = getSecurityPolicy().createInteraction(participation)
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


