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

$Id: metaconfigure.py,v 1.4 2003/12/19 16:53:17 mchandra Exp $
"""
from zope.app import zapi
from zope.app.interfaces.rdb import IZopeDatabaseAdapter


def connectionhandler(_context, name, component, dsn):
    connection = component(dsn)
    _context.action(
            discriminator = ('provideConnection', name),
            callable = provideConnection,
            args = (name, connection) )
    
def provideConnection(name, connection):
    """ Registers a database connection
    
     Uses the Utility Service for registering
    """
    utilities = zapi.getService(None, zapi.servicenames.Utilities)
    utilities.provideUtility(IZopeDatabaseAdapter, connection, name)


    

