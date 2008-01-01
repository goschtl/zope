##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import zope.interface

class IServerProtocolHandler(zope.interface.Interface):

    def __call__(client_protocol):
        """Return an IServerHandler for the given conection and protocol.
        """

class IClientProtocolHandler(zope.interface.Interface):

    def __call__(server_protocol):
        """Return an IClientHandler for the given conection and protocol.

        The handler.protocol must be less than or equal to the server protocol.
        """

class IBaseHandler(zope.interface.Interface):

    protocol = zope.interface.Attribute("A string giving the handler protocol")

    def handle_connection(connection):
        """Begin communication

        This is called once after the connection has been established.
        """

    def handle_one_way(connection, method, *arguments):
        """Handle a one-way call
        """

    def handle_close(connection, reason):
        """Handle a connection close
        """

IClientHandler = IBaseHandler

class IServerHandler(IBaseHandler):

    def handle_call(server_connection, message_id, method, *arguments):
        """Handle a normal (2-way) call

        The return value is ignored. The handler must later call
        result or exception on the server_connection.
        """

class IBaseConnection(zope.interface.Interface):

    def one_way(method, *arguments):
        """Send a one-way message
        """

    def close():
        """Close the connection
        """

class IClientConnection(IBaseConnection):

    def call(method, *arguments):
        """Call a method on the server, waiting for the result.

        This is a convenience method that returns the result of
        calling the wait method with the result of calling the request
        method.

        The separate request and wait methods are mainly useful for
        testing, although they allow multiple calls to be made
        simultaniously.
        """

    def request(method, *arguments):
        """Start calling a remote method

        A message id is returned. This can be passed to the wait
        method to wait for a result.
        """

    def wait(message_id):
        """Wait for and return a request result.
        """

class IServerConnection(IBaseConnection):

    def result(message_id, value):
        """Return the result of a previous call.
        """

    def exception(message_id, value):
        """Return an exception value
        """



