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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Library for forking storage server and connecting client storage"""

import os
import sys
import types
import random
import socket
import asyncore
import traceback
from cStringIO import StringIO

import ZEO.ClientStorage
import ZConfig
from ZODB import StorageConfig

# Change value of PROFILE to enable server-side profiling
PROFILE = 0
if PROFILE:
    import hotshot

def get_port():
    """Return a port that is not in use.

    Checks if a port is in use by trying to connect to it.  Assumes it
    is not in use if connect raises an exception.

    Raises RuntimeError after 10 tries.
    """
    for i in range(10):
        port = random.randrange(20000, 30000)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            try:
                s.connect(('localhost', port))
            except socket.error:
                # XXX check value of error?
                return port
        finally:
            s.close()
    raise RuntimeError, "Can't find port"

if os.name == "nt":

    # XXX This is probably broken now
    def start_zeo_server(conf, addr=None, ro_svr=0):
        """Start a ZEO server in a separate process.

        Returns the ZEO port, the test server port, and the pid.
        """
        import ZEO.tests.winserver
        if addr is None:
            port = get_port()
        else:
            port = addr[1]
        script = ZEO.tests.winserver.__file__
        if script.endswith('.pyc'):
            script = script[:-1]
        if ro_svr:
            prefix = (sys.executable, script, "-r")
        else:
            prefix = (sys.executable, script)
        args = prefix + (str(port), storage_name) + args
        d = os.environ.copy()
        d['PYTHONPATH'] = os.pathsep.join(sys.path)
        pid = os.spawnve(os.P_NOWAIT, sys.executable, args, d)
        return ('localhost', port), ('localhost', port + 1), pid

else:

    class ZEOServerExit(asyncore.file_dispatcher):
        """Used to exit ZEO.StorageServer when run is done"""

        def writable(self):
            return 0

        def readable(self):
            return 1

        def handle_read(self):
            buf = self.recv(4)
            if buf:
                assert buf == "done"
                server.close_server()
                asyncore.socket_map.clear()

        def handle_close(self):
            server.close_server()
            asyncore.socket_map.clear()

    class ZEOClientExit:
        """Used by client to cause server to exit"""
        def __init__(self, pipe):
            self.pipe = pipe

        def close(self):
            try:
                os.write(self.pipe, "done")
                os.close(self.pipe)
            except os.error:
                pass

    def start_zeo_server(conf, addr, ro_svr=0):
        rd, wr = os.pipe()
        pid = os.fork()
        if pid == 0:
            asyncore.socket_map.clear() # Don't service the parent's sockets
            import ZEO.zrpc.log
            reload(ZEO.zrpc.log) # Don't share the logging file object
            try:
                if PROFILE:
                    p = hotshot.Profile("stats.s.%d" % os.getpid())
                    p.runctx(
                        "run_server(addr, rd, wr, conf, ro_svr)",
                        globals(), locals())
                    p.close()
                else:
                    run_server(addr, rd, wr, conf, ro_svr)
            except:
                print "Exception in ZEO server process"
                traceback.print_exc()
            os._exit(0)
        else:
            os.close(rd)
            return pid, ZEOClientExit(wr)

    def load_storage(conf):
        fp = StringIO(conf)
        rootconf = ZConfig.loadfile(fp)
        storageconf = rootconf.getSection('Storage')
        return StorageConfig.createStorage(storageconf)

    def run_server(addr, rd, wr, conf, ro_svr):
        # in the child, run the storage server
        global server
        os.close(wr)
        ZEOServerExit(rd)
        import ZEO.StorageServer, ZEO.zrpc.server
        storage = load_storage(conf)
        server = ZEO.StorageServer.StorageServer(addr, {'1':storage}, ro_svr)
        ZEO.zrpc.server.loop()
        storage.close()
        if isinstance(addr, types.StringType):
            os.unlink(addr)

    def start_zeo(conf, cache=None, cleanup=None,
                  domain="AF_INET", storage_id="1", cache_size=20000000):
        """Setup ZEO client-server for storage.

        Returns a ClientStorage instance and a ZEOClientExit instance.

        XXX Don't know if os.pipe() will work on Windows.
        """

        if domain == "AF_INET":
            addr = '', get_port()
        elif domain == "AF_UNIX":
            import tempfile
            addr = tempfile.mktemp()
        else:
            raise ValueError, "bad domain: %s" % domain

        pid, exit = start_zeo_server(conf, addr)
        s = ZEO.ClientStorage.ClientStorage(addr, storage_id,
                                            client=cache,
                                            cache_size=cache_size,
                                            min_disconnect_poll=0.5,
                                            wait=1)
        return s, exit, pid
