
import marshal
import os
import time
import ZEO.zrpc.connection


base = '/tmp'

path = None

def log(connection, action=None):
    """Enable, disable, or get the path of the zeo input log
    """
    global path

    if action is None:
        connection.write(path and ("%r\n" % path) or 'disabled')
        return

    if action == 'disable':
        if path is None:
            connection.write("Already disabled\n")
        else:
            connection.write("disabled %r\n" % path)
            del ZEO.zrpc.connection.ManagedServerConnection.message_input
            path = None
        return

    if action != 'enable':
        connection.write("Unknown action: %r\n" % action)

    if path:
        log(connection, 'disable')

    _path = os.path.join(base, time.strftime("%y%m%d%H%M%S",
                                             time.gmtime(time.time())))

    log_file = open(_path, 'w')
    path = _path
    base_message_input = ZEO.zrpc.connection.Connection.message_input
    dump = marshal.dump
    timetime = time.time

    def message_input(self, message):
        dump((id(self), timetime(), message), log_file)
        base_message_input(self, message)

    ZEO.zrpc.connection.ManagedServerConnection.message_input = message_input
    connection.write("enabled %r\n" % path)
