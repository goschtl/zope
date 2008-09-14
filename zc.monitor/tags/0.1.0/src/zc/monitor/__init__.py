##############################################################################
#
# Copyright (c) 2005-2008 Zope Corporation and Contributors.
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
"""Zope 3 Monitor Server
"""

import errno, logging, traceback, socket

import zope.component

import zc.ngi.adapters
import zc.monitor.interfaces

INTERACTIVE_MARKER = object()
QUIT_MARKER = object()

class Server:

    last_command = None

    def __init__(self, connection):
        connection = zc.ngi.adapters.Lines(connection)
        self.connection = connection
        connection.setHandler(self)
        self.mode = QUIT_MARKER

    def handle_input(self, connection, data):
        args = data.strip().split()
        if not args:
            if self.last_command is not None:
                command_name, args = self.last_command
            else:
                return
        else:
            command_name = args.pop(0)
            self.last_command = (command_name, args)
        command = zope.component.queryUtility(
            zc.monitor.interfaces.IMonitorPlugin,
            command_name)
        if command is None:
            connection.write(
                'Invalid command %r\nTry "help".\n' % command_name)
        else:
            try:
                res = command(connection, *args)
            except Exception, v:
                traceback.print_exc(100, connection)
                print >> connection, "%s: %s\n" % (v.__class__.__name__, v)
            if res is INTERACTIVE_MARKER:
                self.mode = res
            elif res is QUIT_MARKER:
                self.mode = res

        if self.mode is QUIT_MARKER:
            connection.write(zc.ngi.END_OF_DATA)


def start(port):
    """start monitor server.
    
    Returns True if monitor server started; returns False if the port is
    already in use; and raises an exception otherwise.
    """
    import zc.ngi.async
    try:
        zc.ngi.async.listener(('', port), Server)
    except socket.error, e:
        if e.args[0] == errno.EADDRINUSE:
            # Don't kill the process just because somebody else has our port.
            # This might be a zopectl debug or some other innocuous problem.
            logging.warning(
                'unable to start z3monitor server because port %d is in use.',
                port)
            return False
        else:
            raise
    return True

# default commands

def interactive(connection):
    """Turn on monitor's interactive mode
    
    Normally, the monitor releases the connection after a single command.
    By entering the interactive mode, the monitor will not end the connection
    until you enter the "quit" command.
    
    In interactive mode, an empty line repeats the last command.
    """
    connection.write('Interactive mode on.  Use "quit" To exit.\n')
    return INTERACTIVE_MARKER

def quit(connection):
    """Quit the monitor
    
    This is only really useful in interactive mode (see the "interactive"
    command).
    """
    connection.write('Goodbye.\n')
    return QUIT_MARKER

def help(connection, command_name=None):
    """Get help about server commands

    By default, a list of commands and summaries is printed.  Provide
    a command name to get detailed documentation for a command.
    """
    if command_name is None:
        connection.write(str(
            "Supported commands:\n  "
            + '\n  '.join(sorted(
                "%s -- %s" % (name, (u.__doc__ or '?').split('\n', 1)[0])
                for (name, u) in
                zope.component.getUtilitiesFor(
                    zc.monitor.interfaces.IMonitorPlugin)))
            + '\n'))
    else:
        command = zope.component.getUtility(
            zc.monitor.interfaces.IMonitorPlugin,
            command_name)
        connection.write("Help for %s:\n\n%s\n"
                         % (command_name, command.__doc__)
                         )
