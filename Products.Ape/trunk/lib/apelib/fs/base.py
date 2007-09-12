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
"""Base implementation for FS gateways.

$Id$
"""

class FSGatewayBase:
    """Base implementation for FS gateways."""

    schema = None

    def __init__(self, conn_name='fs'):
        self.conn_name = conn_name

    def get_connection(self, event):
        return event.connections[self.conn_name]

    def get_sources(self, event):
        return None
