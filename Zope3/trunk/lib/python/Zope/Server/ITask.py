# Copyright 2001-2002 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.


from Interface import Interface


class ITask (Interface):
    """
    The interface expected of an object placed in the queue of
    a ThreadedTaskDispatcher.  Provides facilities for executing
    or canceling the task.
    """

    def service():
        """
        Services the task.  Either service() or cancel() is called
        for every task queued.
        """

    def cancel():
        """
        Called instead of service() during shutdown or if an
        exception occurs that prevents the task from being
        serviced.  Must return quickly and should not throw exceptions.
        """

    def defer():
        """
        Called just before the task is queued to be executed in
        a different thread.
        """
