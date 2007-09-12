##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Standard oid generators.

$Id$
"""

from apelib.core.interfaces import IOIDGenerator, IGatewayEvent


class SerialOIDGenerator:
    """Minimal OID generator that generates OIDs in series.

    Does not store the counter in non-volatile storage.
    """
    __implements__ = IOIDGenerator

    root_oid = '0'
    counter = 1

    def __init__(self, root_oid="0"):
        self.root_oid = root_oid

    def new_oid(self, event):
        assert IGatewayEvent.isImplementedBy(event)
        oid = str(self.counter)
        self.counter += 1
        return oid
