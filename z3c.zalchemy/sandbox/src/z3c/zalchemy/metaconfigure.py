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

def engine(_context, name, dns, echo=False, **kwargs):
    component = AlchemyEngineUtility(name, dns, echo, **kwargs)
    utility(_context,
            IAlchemyEngineUtility,
            component,
            permission=PublicPermission,
            name=name)

def connect(_context, engine, table):
    _context.action(
            discriminator = (engine, table),
            callable = connector,
            args = (engine, table)
            )

def connector(engine, table):
    util = component.getUtility(IAlchemyEngineUtility, engine)
    util.addTable(table)
    #connections.append((util, table))

