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

import cPickle
import cStringIO
import logging
import sys
import threading

import zc.ngi.adapters
import zope.interface

logger = logging.getLogger(__name__)

class RPCError(Exception):
    """An error in the RPC protocol
    """

class BadGlobal(RPCError):
    """No such module
    """

class Closed(RPCError):
    """An attempt was made to send or recieve data on a closed connection.
    """

class _BaseConnection:

    def __init__(self, connection, protocol_handler):
        connection = zc.ngi.adapters.Sized(connection)
        self._connection = connection
        self._protocol_handler = protocol_handler
        connection.setHandler(self)

    def handle_input(self, connection, data):
        try:
            handler = self._handler
        except AttributeError:
            self._handle_protocol(data)
            self._handler.handle_connection(self)
            return

        unpickler = cPickle.Unpickler(cStringIO.StringIO(data))
        unpickler.find_global = self._find_global
        message_id, one_way, method_name, arguments = unpickler.load()
        if one_way:
            handler.handle_one_way(self, method_name, *arguments)
        else:
            self._handle_message(message_id, method_name, arguments)

    _closed = False
    def close(self):
        self._closed = True
        self._connection.close()

    def handle_close(self, connection, reason):
        self._closed = True
        try:
            handler = self._handler
        except AttributeError:
            pass
        else:
            handler.handle_close(self, reason)

    def one_way(self, method, *arguments):
        if self._closed:
            raise Closed
        self._connection.write(cPickle.dumps((0, 1, method, arguments), 1))

class ServerConnection(_BaseConnection):
    _find_global = None

    def __init__(self, connection, protocol_handler, protocol=None):
        if protocol is None:
            protocol = protocol_handler.protocol
        _BaseConnection.__init__(self, connection, protocol_handler)
        self._connection.write(protocol)

    def _handle_protocol(self, protocol):
        self._handler = self._protocol_handler(protocol)
        
    def _handle_message(self, message_id, meth, arguments):
        try:
            self._handler.handle_call(self, message_id, meth, arguments)
        except:
            self.exception(message_id, sys.exc_info()[1])

    def result(self, message_id, value):
        if self._closed:
            raise Closed
        self._connection.write(
            cPickle.dumps((message_id, 0, '.reply', value), 1)
            )

    def exception(self, message_id, value):
        if self._closed:
            raise Closed
        value = value.__class__, value
        self._connection.write(
            cPickle.dumps((message_id, 0, '.reply', value), 1)
            )

class ClientConnection(_BaseConnection):

    def __init__(self, connection, protocol_handler):
        _BaseConnection.__init__(self, connection, protocol_handler)
        self._replies = {}
        self._cond = threading.Condition()
        self._message_id_lock = threading.Lock()

    def _handle_protocol(self, protocol):
        self._handler = self._protocol_handler(protocol)
        self._connection.write(self._handler.protocol)

    def _handle_message(self, message_id, meth, arguments):
        if meth != '.reply':
            logger.critical("Unexpected cliet call")
            self.close()
            self._handler.handle_close("Bad Server")
        else:
            cond = self._cond
            cond.acquire()
            try:
                self._replies[message_id] = arguments
                cond.notifyAll()
            finally:
                cond.release()

    def _next_message_id(self):
        self._lock.acquire()
        try:
            self._message_id = message_id = self._message_id + 1
            return message_id
        finally:
            self._lock.release()

    _message_id = 0
    def request(self, method, *arguments):
        if self._closed:
            raise Closed
        self._message_id_lock.acquire()
        try:
            self._message_id = message_id = self._message_id + 1
        finally:
            self._message_id_lock.release()
        self._connection.write(
            cPickle.dumps((message_id, 0, method, arguments))
            )
        return message_id

    def wait(self, message_id):
        if self._closed:
            raise Closed
        cond = self._cond
        replies = self._replies
        cond.acquire()
        try:
            while 1:
                try:
                    if self._closed:
                        raise Closed
                    result = replies.pop(message_id)
                except KeyError:
                    pass
                else:
                    break
                cond.wait()
        finally:
            cond.release()

        if (isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[1], Exception)):
            raise result[1]
        return result

    def call(self, meth, *args):
        return self.wait(self.request(meth, *args))

    def _find_global(self, module_name, name):
        # Find a global, which must be an exception subclass

        try:
            module = sys.modules[module_name]
        except KeyError:
            raise BadGlobal(module_name, name)

        try:
            r = getattr(module, name)
        except AttributeError:
            raise BadGlobal(module_name, name)

        if issubclass(r, Exception):
            return r

        raise BadGlobal(module_name, name)
    
