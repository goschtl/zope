# Copyright 2001-2002 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.


from Interface import Interface

class ITaskDispatcher (Interface):
    """An object that accepts tasks and dispatches them to threads.
    """

    def setThreadCount(count):
        """Sets the number of handler threads.
        """

    def addTask(task):
        """Receives a task and dispatches it to a thread.

        Note that, depending on load, a task may have to wait a
        while for its turn.
        """

    def shutdown(cancel_pending=1, timeout=5):
        """Shuts down all handler threads and may cancel pending tasks.
        """

    def getPendingTasksEstimate():
        """Returns an estimate of the number of tasks waiting to be serviced.

        This method may be useful for monitoring purposes.  If the
        number of pending tasks is continually climbing, your server
        is becoming overloaded and the operator should be notified.
        """

