"""Helper file used to launch ZEO server for Windows tests"""

import asyncore
import os
import random
import socket
import threading
import types

import ZEO.StorageServer

class ZEOTestServer(asyncore.dispatcher):
    """A trivial server for killing a server at the end of a test

    The server calls os._exit() as soon as it is connected to.  No
    chance to even send some data down the socket.
    """
    __super_init = asyncore.dispatcher.__init__

    def __init__(self, addr):
        self.__super_init()
        if type(addr) == types.StringType:
            self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(addr)
        self.listen(5)

    def handle_accept(self):
        sock, addr = self.accept()
        os._exit(0)

def load_storage_class(name):
    package = __import__("ZODB." + name)
    mod = getattr(package, name)
    return getattr(mod, name)

def main(port, storage_name, args):
    klass = load_storage_class(storage_name)
    storage = klass(*args)
    zeo_port = int(port)
    test_port = zeo_port + 1
    t = ZEOTestServer(('', test_port))
##    t = threading.Thread(target=ZEOTestServer, args=(('', test_port),))
##    t.start()
    serv = ZEO.StorageServer.StorageServer(('', zeo_port), {'1': storage})
    asyncore.loop()

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
