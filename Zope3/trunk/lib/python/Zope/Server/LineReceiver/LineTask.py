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
"""

$Id: LineTask.py,v 1.2 2002/06/10 23:29:36 jim Exp $
"""

import socket
import time
from Zope.Server.ITask import ITask


class LineTask:
    """This is a generic task that can be used with command line
       protocols to handle commands in a separate thread.
    """

    __implements__ = ITask


    def __init__(self, channel, command, m_name):
        self.channel = channel
        self.m_name = m_name
        self.args = command.args

        self.close_on_finish = 0


    ############################################################
    # Implementation methods for interface
    # Zope.Server.ITask

    def service(self):
        """Called to execute the task.
        """
        try:
            try:
                self.start()
                getattr(self.channel, self.m_name)(self.args)
                self.finish()
            except socket.error:
                self.close_on_finish = 1
                if self.channel.adj.log_socket_errors:
                    raise
            except:
                self.channel.exception()
        finally:
            self.channel.end_task(self.close_on_finish)


    def cancel(self):
        'See Zope.Server.ITask.ITask'
        self.channel.close_when_done()


    def defer(self):
        'See Zope.Server.ITask.ITask'
        pass

    #
    ############################################################

    def start(self):
        now = time.time()
        self.start_time = now


    def finish(self):
        hit_log = self.channel.server.hit_log
        if hit_log is not None:
            hit_log.log(self)
