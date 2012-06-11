##############################################################################
#
# Copyright (c) 2001,2002,2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Server Control Implementation

$Id$
"""

from twisted.internet import reactor

from zope.app.applicationcontrol.interfaces import IServerControl
from zope.app.twisted import main
from zope.interface import implements


class ServerControl(object):

    implements(IServerControl)

    def shutdown(self, time=0):
        """See zope.app.applicationcontrol.interfaces.IServerControl"""
        # This will work for servers started directly and by zdaemon.
        reactor.callLater(time, reactor.stop)

    def restart(self, time=0):
        """See zope.app.applicationcontrol.interfaces.IServerControl"""
        # TODO: Make sure this is only called if we are running via zdaemon.
        # Setting the module global variable in the main module signals zdaemon to restart
        main.should_restart = True
        reactor.callLater(time, reactor.stop)

serverControl = ServerControl()
