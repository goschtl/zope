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
"""Stub for interface exported by ClientStorage"""

class ClientStorage:

    # The on-the-wire names of some of the methods don't match the
    # Python method names.  That's because the on-the-wire protocol
    # was fixed for ZEO 2 and we don't want to change it.  There are
    # some aliases in ClientStorage.py to make up for this.

    def __init__(self, rpc):
        self.rpc = rpc

    def beginVerify(self):
        self.rpc.callAsync('begin')

    def invalidateVerify(self, args):
        self.rpc.callAsync('invalidate', args)

    def endVerify(self):
        self.rpc.callAsync('end')

    def invalidateTrans(self, args):
        self.rpc.callAsync('Invalidate', args)

    def serialnos(self, arg):
        self.rpc.callAsync('serialnos', arg)

    def info(self, arg):
        self.rpc.callAsync('info', arg)
