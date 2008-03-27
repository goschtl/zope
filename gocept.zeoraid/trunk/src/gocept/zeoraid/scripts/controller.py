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
"""

import sys

import ZEO.zrpc.client

import logging
logging.getLogger().addHandler(logging.StreamHandler())

class RAIDManager(object):

    def __init__(self):
        self.manager = ZEO.zrpc.client.ConnectionManager(('127.0.0.1', 8100), self)
        self.manager.connect(True)

    def testConnection(self, connection):
        # This is a preferred connection
        return 1

    def notifyConnected(self, connection):
        self.connection = connection
        self.connection.call('register', '1', True)

    def status(self):
        return self.connection.call('raid_status')

    def recover(self, storage):
        return self.connection.call('raid_recover', storage)

    def disable(self, storage):
        return self.connection.call('raid_disable', storage)

    def details(self):
        return self.connection.call('raid_details')

if __name__ == '__main__':
    m = RAIDManager()

    if sys.argv[1] == 'status':
        print m.status()
    elif sys.argv[1] == 'details':
        ok, recovering, failed = m.details()
        print "RAID status:"
        print "\t", m.status()
        print "Storage status:"
        print "\toptimal\t\t", ok
        print "\trecovering\t", recovering
        print "\tfailed\t\t", failed
    elif sys.argv[1] == 'disable':
        print m.disable(sys.argv[2])
    elif sys.argv[1] == 'recover':
        print m.recover(sys.argv[2])
