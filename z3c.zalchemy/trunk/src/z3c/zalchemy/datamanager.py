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

import transaction
from zope.interface import implements
from zope.component import queryUtility, getUtility, getUtilitiesFor

from transaction.interfaces import IDataManager, ISynchronizer

from interfaces import IAlchemyEngineUtility

import sqlalchemy


class AlchemyEngineUtility(object):
    """A utility providing a database engine.
    """
    implements(IAlchemyEngineUtility)

    def __init__(self, name, url, echo=False, **kwargs):
        self.name = name
        self.url = url
        self.echo = echo
        self.kw={}
        self.kw.update(kwargs)
        self.storage = local()

    def getEngine(self):
        engine = getattr(self.storage,'engine',None)
        if engine:
            return engine
        # create_engine consumes the keywords, so better to make a copy first
        kw = {}
        kw.update(self.kw)
        # create a new engine and store it thread local
        self.storage.engine = sqlalchemy.create_engine(self.url,
                                            echo=self.echo,
                                            **kw)
        return self.storage.engine

    def _resetEngine(self):
        self.storage.engine=None


metadata = sqlalchemy.MetaData()

_tableToEngine = {}
_classToEngine = {}
_tablesToCreate = []
_storage = local()

def getSession(createTransaction=False):
    session=getattr(_storage,'session',None)
    if session:
        return session
    txn = transaction.manager.get()
    if createTransaction and (txn is None):
        txn = transaction.begin()
    util = queryUtility(IAlchemyEngineUtility)
    engine = None
    if util is not None:
        engine = util.getEngine()
    _storage.session=sqlalchemy.create_session(bind_to=engine)
    session = _storage.session
    for table, engine in _tableToEngine.iteritems():
        _assignTable(table, engine)
    for class_, engine in _classToEngine.iteritems():
        _assignClass(class_, engine)
    if txn is not None:
        _storage.dataManager = AlchemyDataManager(session)
        txn.join(_storage.dataManager)
    _createTables()
    return session


def getEngineForTable(t):
    name = _tableToEngine[t]
    util = getUtility(IAlchemyEngineUtility, name=name)
    return util.getEngine()
    

def inSession():
    return getattr(_storage,'session',None) is not None


def assignTable(table, engine):
    _tableToEngine[table]=engine
    _assignTable(table, engine)


def assignClass(class_, engine):
    _classToEngine[class_]=engine
    _assignClass(class_, engine)


def createTable(table, engine=''):
    _tablesToCreate.append((table, engine))
    _createTables()


def _assignTable(table, engine):
    if inSession():
        t = metadata.tables[table]
        util = getUtility(IAlchemyEngineUtility, name=engine)
        _storage.session.bind_table(t,util.getEngine())


def _assignClass(class_, engine):
    if inSession():
        m = sqlalchemy.orm.session.class_mapper(class_)
        util = getUtility(IAlchemyEngineUtility, name=engine)
        _storage.session.bind_mapper(m,util.getEngine())


def _createTables():
    if inSession():
        tables = _tablesToCreate[:]
        del _tablesToCreate[:]
        for table, engine in tables:
            _doCreateTable(table, engine)


def _doCreateTable(table, engine):
    for t, tengine in _tableToEngine.iteritems():
        if t==table:
            t = metadata.tables[table]
            util = getUtility(IAlchemyEngineUtility, name=tengine)
            try:
                util.getEngine().create(t)
            except:
                pass
            return
    util = getUtility(IAlchemyEngineUtility, name=engine)
    t = metadata.tables[table]
    try:
        util.getEngine().create(t)
    except:
        pass


def dropTable(table, engine=''):
    for t, tengine in _tableToEngine.iteritems():
        if t==table:
            t = metadata.tables[table]
            util = getUtility(IAlchemyEngineUtility, name=tengine)
            try:
                util.getEngine().drop(t)
            except:
                pass
            return
    util = getUtility(IAlchemyEngineUtility, name=engine)
    t = metadata.tables[table]
    try:
        util.getEngine().drop(t)
    except:
        pass


def _dataManagerFinished():
    _storage.session = None
    _storage.dataManager = None
    utils = getUtilitiesFor(IAlchemyEngineUtility)
    for util in utils:
        util[1]._resetEngine()


class AlchemyDataManager(object):
    """Takes care of the transaction process in zope.
    """
    implements(IDataManager)

    def __init__(self, session):
        self.session = session
        self.transaction = session.create_transaction()

    def abort(self, trans):
        self.transaction.rollback()
        _dataManagerFinished()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        self.transaction.commit()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        _dataManagerFinished()

    def tpc_abort(self, trans):
        self.transaction.rollback()
        _dataManagerFinished()

    def sortKey(self):
        return str(id(self))

