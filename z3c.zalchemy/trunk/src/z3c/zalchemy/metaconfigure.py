##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH
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
from zope import component
from zope.app.component.metaconfigure import utility, PublicPermission

from datamanager import AlchemyEngineUtility
from interfaces import IAlchemyEngineUtility

import z3c.zalchemy

def engine(_context, url, name='', echo=False, **kwargs):
    engine = AlchemyEngineUtility(name, url, echo=echo, **kwargs)
    utility(_context,
            IAlchemyEngineUtility,
            engine,
            permission=PublicPermission,
            name=name)

def connectTable(_context, table, engine):
    z3c.zalchemy.assignTable(table, engine)

def connectClass(_context, class_, engine):
    z3c.zalchemy.assignClass(class_, engine)

def createTable(_context, table):
    z3c.zalchemy.createTable(table)

