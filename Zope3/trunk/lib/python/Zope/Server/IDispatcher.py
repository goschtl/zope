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

$Id: IDispatcher.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from ISocket import ISocket
from IDispatcherEventHandler import IDispatcherEventHandler
from IDispatcherLogging import IDispatcherLogging


class IDispatcher(ISocket, IDispatcherEventHandler, IDispatcherLogging):
    """The dispatcher is the most low-level component of a server.

       1. It manages the socket connections and distributes the
          request to the appropriate channel.

       2. It handles the events passed to it, such as reading input,
          writing output and handling errors. More about this
          functionality can be found in IDispatcherEventHandler.

       3. It handles logging of the requests passed to the server as
          well as other informational messages and erros. Please see
          IDispatcherLogging for more details.

       Note: Most of this documentation is taken from the Python
             Library Reference.
    """

    def add_channel(map=None):
        """After the low-level socket connection negotiation is
           completed, a channel is created that handles all requests
           and responses until the end of the connection.
        """

    def del_channel(map=None):
        """Delete a channel. This should include also closing the
           socket to the client.
        """

    def create_socket(family, type):
        """This is identical to the creation of a normal socket, and
           will use the same options for creation. Refer to the socket
           documentation for information on creating sockets.
        """

    def readable():
        """Each time through the select() loop, the set of sockets is
           scanned, and this method is called to see if there is any
           interest in reading. The default method simply returns 1,
           indicating that by default, all channels will be
           interested.
        """

    def writable():
        """Each time through the select() loop, the set of sockets is
           scanned, and this method is called to see if there is any
           interest in writing. The default method simply returns 1,
           indicating that by default, all channels will be
           interested.
        """
