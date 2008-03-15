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

import persistent
import transaction
from zope.interface import implements

from transaction.interfaces import IDataManager, ISynchronizer
from transaction.interfaces import IDataManagerSavepoint

import z3c.zalchemy.interfaces

import sqlalchemy
import sqlalchemy.orm


class AlchemyEngineUtility(persistent.Persistent):
    """A utility providing a database engine.
    """

    implements(z3c.zalchemy.interfaces.IAlchemyEngineUtility)

    def __init__(self, name, dsn, echo=False, encoding='utf-8',
                 convert_unicode=False, **kwargs):
        self.name = name
        self.dsn = dsn
        self.encoding = encoding
        self.convert_unicode = convert_unicode
        self.echo = echo
        self.kw={}
        self.kw.update(kwargs)

    def getEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine:
            return engine
        # create_engine consumes the keywords, so better to make a copy first
        kw = {}
        kw.update(self.kw)
        # create a new engine and configure it thread-local
        self._v_engine = sqlalchemy.create_engine(
            self.dsn, echo=self.echo, encoding=self.encoding,
            convert_unicode=self.convert_unicode,
            strategy='threadlocal', **kw)
        return self._v_engine

    def _resetEngine(self):
        engine = getattr(self, '_v_engine', None)
        if engine is not None:
            engine.dispose()
            self._v_engine = None


class AlchemyDataManager(object):
    """Takes care of the transaction process in Zope. """

    implements(IDataManager)

    def __init__(self, session):
        self.session = session

    def abort(self, trans):
        self._abort()

    def commit(self, trans):
        # Flush instructions to the database (because of conflict integration)
        self._flush_session()
        # Commit any nested transactions (savepoints)
        while self.session.transaction.nested:
            self.session.commit()

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.session.commit()
        self._cleanup()

    def tpc_abort(self, trans):
        self._abort()

    def sortKey(self):
        return str(id(self))

    def savepoint(self):
        self._flush_session()
        transaction = self.session.begin_nested()
        self._flush_session()
        return AlchemySavepoint(transaction, self.session)

    def _cleanup(self):
        Session.remove()

    def _abort(self):
        while self.session.transaction.nested:
            self.session.transaction.close()
        self.session.rollback()
        self._cleanup()

    def _flush_session(self):
        try:
            self.session.flush()
        except Exception, e:
            conflict = z3c.zalchemy.interfaces.IConflictError(e, None)
            if conflict is None:
                raise
            raise conflict


class AlchemySavepoint(object):
    """A savepoint for the AlchemyDataManager that only supports optimistic
    savepoints.

    """

    implements(IDataManagerSavepoint)

    def __init__(self, transaction, session):
        self.transaction = transaction
        self.session = session

    def rollback(self):
        # Savepoints expire the objects so they get reloaded with the old
        # state
        self.transaction.rollback()
        for obj in self.session:
            self.session.expire(obj)


