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

$Id: IDispatcherEventHandler.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface


class IDispatcherEventHandler(Interface):
    """The Dispatcher can receive several different types of events. This
       interface describes the necessary methods that handle these common
       event types.
    """

    def handle_read_event():
        """Given a read event, a server has to handle the event and
           read the input from the client.
        """

    def handle_write_event():
        """Given a write event, a server has to handle the event and
           write the output to the client.
        """

    def handle_expt_event():
        """An exception event was handed to the server.
        """

    def handle_error():
        """An error occured, but we are still trying to fix it.
        """

    def handle_expt():
        """Handle unhandled exceptions. This is usually a time to log.
        """

    def handle_read():
        """Read output from client.
        """

    def handle_write():
        """Write output via the socket to the client.
        """

    def handle_connect():
        """A client requests a connection, now we need to do soemthing.
        """

    def handle_accept():
        """A connection is accepted.
        """

    def handle_close():
        """A connection is being closed.
        """
