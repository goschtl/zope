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
"""'rdb' ZCML Namespace Directive Handler

$Id: metaconfigure.py,v 1.3 2003/08/17 06:07:45 philikon Exp $
"""
from zope.component import getService
from zope.app.services.servicenames import SQLDatabaseConnections

def connectionhandler(_context, name, component, dsn):
    connection = component(dsn)
    _context.action(
            discriminator = ('provideConnection', name),
            callable = provideConnection,
            args = (name, connection) )

def provideConnection(name, connection):
    getService(None, SQLDatabaseConnections).provideConnection(name, connection)

