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
__doc__ = """ Server Control Interface

$Id: servercontrol.py,v 1.2 2002/12/25 14:12:57 jim Exp $"""

from zope.interface import Interface

class ServerControlError(Exception):
    """Represents an error in the ServerControl.
    """

class DoublePriorityError(ServerControlError):
    """Raisen when somebody tries to register a second Hook
       for a priority."""

class NotCallableError(ServerControlError):
    """Raisen if a given object is not callable."""

class IServerControl(Interface):
    """Server Control Interface defines methods for shutting down and
       restarting the server.

       This utility also keeps a registry of things to call when shutting down
       zope. You can register using this interface or the zcml on the global
       ServerController instance."""

    def shutdown():
        """Shutdown the server gracefully

                Returns: Nothing
        """

    def restart():
        """Restart the server gracefully

                Returns: Nothing
        """

    def registerShutdownHook(call, priority, name):
        """Register a function that will be callen on server shutdown.
           The function needs to takes no argument at all."""
