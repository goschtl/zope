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

$Id: IServerChannel.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute

class IServerChannel(Interface):
    """
    """

    parser_class = Attribute("Subclasses must provide a parser class")
    task_class = Attribute("Subclasses must provide a task class.")

    active_channels = Attribute("Class-specific channel tracker")
    next_channel_cleanup = Attribute("Class-specific cleanup time")

    proto_request = Attribute("A request parser instance")
    ready_requests = Attribute("A list of requests to be processed.")
    last_activity = Attribute("Time of last activity")
    running_tasks = Attribute("boolean")


    def queue_request(self, req):
        """Queues a request to be processed in sequence by a task.
        """

    def end_task(self, close):
        """Called at the end of a task, may launch another task.
        """

    def create_task(self, req):
        """Creates a new task and queues it for execution.

        The task may get executed in another thread.
        """

