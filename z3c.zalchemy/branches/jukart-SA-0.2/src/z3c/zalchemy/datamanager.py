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

from z3c.zalchemy import tableToUtility, tablesToCreate


class AlchemyEngineUtility(object):
    """A utility providing the dns for alchemy database engines.
    """
    implements(IAlchemyEngineUtility)

    def __init__(self, name, dns, echo=False, **kwargs):
        self.name = name
        self.dns = dns
        self.echo = echo
        self.kw={}
        self.kw.update(kwargs)
        self.storage = local()
        self._proxyEngine=sqlalchemy.ext.proxy.ProxyEngine()

    def addTable(self, name):
        if name in tableToUtility:
            #TODO: should raise an exception here
            return
        tableToUtility[name]=self

    def getProxyEngine(self):
        return self._proxyEngine
    proxyEngine = property(getProxyEngine)

    def connectTablesForThread(self):
        # create a thread local engine
        engine=getattr(self.storage,'engine',None)
        if engine is not None:
            return
        # create_engine consumes the keywords, so better to make a copy first
        kw = {}
        kw.update(self.kw)
        # create a new engine and store it thread local
        self.storage.engine = create_engine(self.dns,
                                            kw,
                                            echo=self.echo)
        engine = self.storage.engine
        if self.echo:
            engine.log('adding data manager for %s,%s'%(self.name, self.dns))
        # create a data manager
        self.storage.dataManager = AlchemyDataManager(self)
        txn = manager.get()
        txn.join(self.storage.dataManager)
        # connect the tables to the engine
        self._proxyEngine.engine=engine
        tables = list(tablesToCreate)
        # create tables for this engine :
        for table in tables:
            if table.engine == self._proxyEngine:
                try:
                    table.create()
                except:
                    pass
                tablesToCreate.remove(table)

    def dataManagerFinished(self):
        self.storage.engine=None
        # disconnect the tables from the engine
        self._proxyEngine.engine=None

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
        self.session = objectstore.begin()

    def abort(self, trans):
        self.session.rollback()
        objectstore.clear()
        self.util.dataManagerFinished()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        self.session.commit()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        if self.util.echo:
            self.engine.log('commit for %s'%self.util.name)
        objectstore.clear()
        self.util.dataManagerFinished()

    def tpc_abort(self, trans):
        self.session.rollback()
        objectstore.clear()
        self.util.dataManagerFinished()

    def sortKey(self):
        return str(id(self))

def beforeTraversal(event):
    utils = getUtilitiesFor(IAlchemyEngineUtility)
    for name, util in utils:
        util.connectTablesForThread()

