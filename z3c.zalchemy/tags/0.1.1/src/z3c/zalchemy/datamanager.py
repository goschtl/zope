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

import persistent
import transaction
from zope.interface import implements
from zope.component import queryUtility, getUtility, getUtilitiesFor
from zope.schema.fieldproperty import FieldProperty

from transaction.interfaces import IDataManager, ISynchronizer

from interfaces import IAlchemyEngineUtility

import sqlalchemy


class AlchemyEngineUtility(persistent.Persistent):
    """A utility providing a database engine.
    """
    implements(IAlchemyEngineUtility)

    def __init__(self, name, dsn, echo=False, encoding='utf-8', convert_unicode=False, **kwargs):
        self.name = name
        self.dsn = dsn
        self.encoding = encoding
        self.convert_unicode = convert_unicode
        self.echo = echo
        self.kw={}
        self.kw.update(kwargs)

    def getEngine(self):
        engine = getattr(self.storage,'engine',None)
        if engine:
            return engine
        # create_engine consumes the keywords, so better to make a copy first
        kw = {}
        kw.update(self.kw)
        # create a new engine and store it thread local
        self.storage.engine = sqlalchemy.create_engine(self.dsn,
                                            echo=self.echo,
                                            encoding=self.encoding,
                                            convert_unicode=self.convert_unicode,
                                            **kw)
        return self.storage.engine

    def _resetEngine(self):
        engine = getattr(self.storage, 'engine', None)
        if engine is not None:
            engine.dispose()
            self.storage.engine = None

    @property
    def storage(self):
        if not hasattr(self, '_v_storage'):
            self._v_storage = local()
        return self._v_storage

for name in IAlchemyEngineUtility:
    setattr(AlchemyEngineUtility, name, FieldProperty(IAlchemyEngineUtility[name]))


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


def createTable(table, engine):
    _tablesToCreate.append((table, engine))
    _createTables()


def _assignTable(table, engine):
    if inSession():
        t = metadata.getTable(engine, table, True)
        util = getUtility(IAlchemyEngineUtility, name=engine)
        _storage.session.bind_table(t,util.getEngine())


def _assignClass(class_, engine):
    if inSession():
        m = sqlalchemy.orm.class_mapper(class_)
        util = getUtility(IAlchemyEngineUtility, name=engine)
        _storage.session.bind_mapper(m,util.getEngine())


def _createTables():
    if inSession():
        tables = _tablesToCreate[:]
        del _tablesToCreate[:]
        for table, engine in tables:
            _doCreateTable(table, engine)


def _doCreateTable(table, engine):
    util = getUtility(IAlchemyEngineUtility, name=engine)
    t = metadata.getTable(engine, table, True)
    try:
        util.getEngine().create(t)
    except:
        pass


def dropTable(table, engine=''):
    util = getUtility(IAlchemyEngineUtility, name=engine)
    t = metadata.getTable(engine, table, True)
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

    _commitFailed = False

    def __init__(self, session):
        self.session = session
        self.transaction = session.create_transaction()

    def abort(self, trans):
        self.transaction.rollback()
        _dataManagerFinished()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        self.session.flush()

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.transaction.commit()
        _dataManagerFinished()

    def tpc_abort(self, trans):
        self.transaction.rollback()
        _dataManagerFinished()

    def sortKey(self):
        return str(id(self))


class MetaManager(object):
    """A manager for metadata to be able to use the same table name in
    different databases.
    """

    def __init__(self):
        self.metadata = {}

    def getTable(self, engine, table, fallback):
        md = self.metadata.get(engine)
        if md and table in md.tables:
            return md.tables[table]
        if fallback and engine:
            md = self.metadata.get('')
        if md and table in md.tables:
            return md.tables[table]
        return None

    def __call__(self, engine=''):
        md = self.metadata.get(engine)
        if md is None:
            md = self.metadata[engine] = sqlalchemy.MetaData()
        return md


metadata = MetaManager()

