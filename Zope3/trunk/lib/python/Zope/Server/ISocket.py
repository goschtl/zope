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

$Id: ISocket.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from Interface import Interface


class ISocket(Interface):
    """Represents a socket.

       Note: Most of this documentation is taken from the Python Library
             Reference.
    """

    def listen(num):
        """Listen for connections made to the socket. The backlog argument
           specifies the maximum number of queued connections and should
           be at least 1; the maximum value is system-dependent (usually
           5).
        """

    def bind(addr):
        """Bind the socket to address. The socket must not already be bound.
        """

    def connect(address):
        """Connect to a remote socket at address.
        """

    def accept():
        """Accept a connection. The socket must be bound to an address and
           listening for connections. The return value is a pair (conn,
           address) where conn is a new socket object usable to send and
           receive data on the connection, and address is the address
           bound to the socket on the other end of the connection.
        """

    def recv(buffer_size):
        """Receive data from the socket. The return value is a string
           representing the data received. The maximum amount of data
           to be received at once is specified by bufsize. See the
           Unix manual page recv(2) for the meaning of the optional
           argument flags; it defaults to zero.
        """

    def send(data):
        """Send data to the socket. The socket must be connected to a
           remote socket. The optional flags argument has the same
           meaning as for recv() above. Returns the number of bytes
           sent. Applications are responsible for checking that all
           data has been sent; if only some of the data was
           transmitted, the application needs to attempt delivery of
           the remaining data.
        """

    def close():
        """Close the socket. All future operations on the socket
           object will fail. The remote end will receive no more data
           (after queued data is flushed). Sockets are automatically
           closed when they are garbage-collected.
        """
