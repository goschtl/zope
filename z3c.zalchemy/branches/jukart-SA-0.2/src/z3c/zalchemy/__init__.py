##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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

tableToUtility = {}
tablesToCreate = []

def getProxyEngine(name):
    return tableToUtility[name].proxyEngine

def registerTableForCreation(table):
    """Register a table for later creation.

    The table will be created at the next start of a transaction.

    Usually this will be called immediately after defining the table.
    table must be a sqlalchemy.Table object.
    """
    if table not in tablesToCreate:
        tablesToCreate.append(table)

