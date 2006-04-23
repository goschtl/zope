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
import thread
from threading import local
from ZODB.utils import WeakSet

from zope.interface import implements
from zope.component import getUtilitiesFor

from transaction import get, manager
from transaction.interfaces import IDataManager, ISynchronizer

from interfaces import IAlchemyEngineUtility

from sqlalchemy import objectstore, create_engine
import sqlalchemy


class AlchemyEngineUtility(object):
    """A utility providing the dns for alchemy database engines.
    """
    implements(IAlchemyEngineUtility)

    def __init__(self, name, dns, echo=False, **kwargs):
        self.name = name
        self.dns = dns
        self.echo = echo
        self.kw=kwargs
        self.tables = []
        self.storage = local()
        self.createdTables = {}

    def addTable(self, table, create=False):
        if not isinstance(table.engine, sqlalchemy.ext.proxy.ProxyEngine):
            raise TypeError(table.engine)
        utils = getUtilitiesFor(IAlchemyEngineUtility)
        for name, util in utils:
            if table in util.tables:
                #TODO: should raise an exception here
                return
        self.tables.append(table)
        if create:
            self.createTable(table)

    def createTable(self,table):

        """tries to create the given table if not there"""
        self.connectTablesForThread()
        #table.engine.connect(self.dns,self.kw,echo=self.echo)
        #table.engine.engine = self.storage.engine
        table.create()
        # seems that this does not get commited, why?
        objectstore.commit()
        #self.dataManagerFinished()

        
    def initEngine(self):

        """create a thread local engine if not there, returns True if
        a new engine is created"""
        
        engine=getattr(self.storage,'engine',None)
        if engine is not None:
            return False
        self.storage.engine = create_engine(self.dns,
                                            self.kw,
                                            echo=self.echo)
        return True

    def connectTablesForThread(self):
        # create a thread local engine
        #import pdb;pdb.set_trace()

        self.initEngine()
        if getattr(self.storage,'_connected',False):
            return

        engine = self.storage.engine
        if self.echo:
            engine.log('adding data manager for %s'%self.name)
        # create a data manager
        self.storage.dataManager = AlchemyDataManager(self)
        txn = manager.get()
        txn.join(self.storage.dataManager)
        # connect the tables to the engine
        for table in self.tables:
            table.engine.engine = engine

        self.storage._connected=True

    def dataManagerFinished(self):
        self.storage.engine=None
        self.storage._connected=False
        # disconnect the tables from the engine
        for table in self.tables:
            table.engine.engine = None

    def getEngine(self):
        return getattr(self.storage,'engine',None)
    engine = property(getEngine)


class AlchemyDataManager(object):
    """Takes care of the transaction process in zope.
    """
    implements(IDataManager)

    vote = False

    def __init__(self, util):
        self.util = util
        self.engine = util.getEngine()
        self.engine.begin()

    def abort(self, trans):
        self.engine.rollback()
        objectstore.clear()
        self.util.dataManagerFinished()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        objectstore.commit()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.engine.commit()
        if self.util.echo:
            self.engine.log('commit for %s'%self.util.name)
        objectstore.clear()
        self.util.dataManagerFinished()

    def tpc_abort(self, trans):
        self.engine.rollback()
        objectstore.clear()
        self.util.dataManagerFinished()

    def sortKey(self):
        return str(id(self))

def beforeTraversal(event):
    utils = getUtilitiesFor(IAlchemyEngineUtility)
    for name, util in utils:
        util.connectTablesForThread()

