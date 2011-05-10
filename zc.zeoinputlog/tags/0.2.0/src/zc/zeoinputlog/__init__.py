
import marshal
import os
import time
import ZEO.zrpc.connection


base = '/tmp'

path = None
log_file = None

def log(connection, action=None):
    """Enable, disable, or get the path of the zeo input log
    """
    global path, log_file

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
            try:
                log_file.close()
            finally:
                log_file = None

        return

    if action != 'enable':
        connection.write("Unknown action: %r\n" % action)

    if path:
        log(connection, 'disable')

    _path = os.path.join(base, time.strftime("%y%m%d%H%M%S",
                                             time.gmtime(time.time())))

    # empty log file
    log_file = open(_path, 'w')
    log_file.close()

    # reopen in append mode.  Nort sure this is necessary...
    log_file = open(_path, 'a')
    path = _path
    base_message_input = ZEO.zrpc.connection.Connection.message_input
    dumps = marshal.dumps
    write = log_file.write
    timetime = time.time

    def message_input(self, message):
        write(dumps((id(self), timetime(), message)))
        base_message_input(self, message)

    ZEO.zrpc.connection.ManagedServerConnection.message_input = message_input
    connection.write("enabled %r\n" % path)
