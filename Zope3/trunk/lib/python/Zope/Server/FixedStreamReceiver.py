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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: FixedStreamReceiver.py,v 1.2 2002/06/10 23:29:34 jim Exp $
"""

from IStreamConsumer import IStreamConsumer


class FixedStreamReceiver:

    __implements__ = IStreamConsumer

    # See Zope.Server.IStreamConsumer.IStreamConsumer
    completed = 0

    def __init__(self, cl, buf):
        self.remain = cl
        self.buf = buf

    ############################################################
    # Implementation methods for interface
    # Zope.Server.IStreamConsumer

    def received(self, data):
        'See Zope.Server.IStreamConsumer.IStreamConsumer'
        rm = self.remain
        if rm < 1:
            self.completed = 1  # Avoid any chance of spinning
            return 0
        datalen = len(data)
        if rm <= datalen:
            self.buf.append(data[:rm])
            self.remain = 0
            self.completed = 1
            return rm
        else:
            self.buf.append(data)
            self.remain -= datalen
            return datalen

    #
    ############################################################

    def getfile(self):
        return self.buf.getfile()
