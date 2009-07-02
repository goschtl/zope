##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and contributors.
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
"""The management utility for gocept.zeoraid.

Usage: controller.py [options] <command> [command_options]

Options:

    -p port -- port to connect to (default is 8100)

    -h host -- host to connect to (default is 127.0.0.1)

    -S name -- storage name (default is '1')

Commands:

    status -- Print short status information

    details -- Print detailed status information

    recover <storage> -- Start recovery for a storage

    disable <storage> -- Disable a storage

    reload </path/to/zeo.conf> -- Reload a specified zeo.conf file

"""

import optparse
import sys

import ZEO.ClientStorage

import logging


class RAIDManager(object):

    def __init__(self, host, port, storage):
        self.host = host
        self.port = port
        self.storage = storage

        self.raid = ZEO.ClientStorage.ClientStorage(
            (self.host, self.port), storage=self.storage, wait=1, read_only=1)

    def cmd_status(self):
        print self.raid.raid_status()

    def cmd_details(self):
        ok, recovering, failed = self.raid.raid_details()
        print "RAID status:"
        print "\t", self.raid.raid_status()
        print "Storage status:"
        print "\toptimal\t\t", ok
        print "\trecovering\t", recovering
        print "\tfailed\t\t", failed

    def cmd_recover(self, storage):
        print self.raid.raid_recover(storage)

    def cmd_disable(self, storage):
        print self.raid.raid_disable(storage)

    def cmd_reload(self, path):
        print self.raid.raid_reload(path)

def main(host="127.0.0.1", port=8100, storage="1"):
    usage = "usage: %prog [options] command [command-options]"
    description = ("Connect to a RAIDStorage on a ZEO server and perform "
                   "maintenance tasks. Available commands: status, details, "
                   "recover <STORAGE>, disable <STORAGE>, reload </PATH/TO/ZEO.CONF>")

    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option("-S", "--storage", default=storage,
                      help="Use STORAGE on ZEO server. Default: %default")
    parser.add_option("-H", "--host", default=host,
                      help="Connect to HOST. Default: %default")
    parser.add_option("-p", "--port", type="int", default=port,
                      help="Connect to PORT. Default: %default")
    options, args = parser.parse_args()

    if not args:
        parser.error("no command given")

    command, subargs = args[0], args[1:]

    logging.getLogger().addHandler(logging.StreamHandler())
    m = RAIDManager(options.host, options.port, options.storage)
    command = getattr(m, 'cmd_%s' % command)
    command(*subargs)


if __name__ == '__main__':
    main()
