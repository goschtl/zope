##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) Zope Corporation and Contributor
# Written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
# and ZOPYX Ltd. & Co. KG, Tuebingen, Germany
##########################################################################

import threading

import sqlalchemy
from sqlalchemy.engine.url import make_url

from zope.interface import implements
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper, IModelProvider
from z3c.sqlalchemy.model import Model
from z3c.sqlalchemy.mapper import LazyMapperCollection

import transaction
from transaction.interfaces import IDataManager


class SynchronizedThreadCache(object):

    def __init__(self):
        self.lock = threading.Lock()
        self.cache = threading.local()


    def set(self, **kw):
        self.lock.acquire()
        for k,v in kw.items():
            setattr(self.cache, k, v)
        self.lock.release()


    def get(self, *names):
        self.lock.acquire()
        result = [getattr(self.cache, name, None) for name in names]
        self.lock.release()
        return result


class BaseWrapper(object):

    implements(ISQLAlchemyWrapper)

    def __init__(self, dsn, model=None, **kw):
        """ 'dsn' - a RFC-1738-style connection string

            'model' - optional instance of model.Model

            'kw' - optional keyword arguments passed to create_engine()
        """

        self.dsn = dsn
        self.url = make_url(dsn)
        self.host = self.url.host
        self.port = self.url.port
        self.username = self.url.username
        self.password = self.url.password
        self.dbname = self.url.database 
        self.drivername = self.url.drivername
        self.kw = kw
        self.echo = kw.get('echo', False)
        self._model = None
        self._createEngine()

        if model:

            if isinstance(model, Model):
                self._model = model

            elif isinstance(model, basestring):

                try:
                    util = getUtility(IModelProvider, model)
                except ComponentLookupError:
                    raise ComponentLookupError("No named utility '%s' providing IModelProvider found" % model)


                self._model = util.getModel(self.metadata)

            elif callable(model):                        

                self._model = model(self.metadata)


            else:
                raise ValueError("The 'model' parameter passed to constructor must either be "\
                                 "the name of a named utility implementing IModelProvider or "\
                                 "an instance of z3c.sqlalchemy.model.Model.")

            if not isinstance(self._model, Model):
                raise TypeError('_model is not an instance of model.Model')


        # mappers must be initialized at last since we need to acces
        # the 'model' from within the constructor of LazyMapperCollection
        self._mappers = LazyMapperCollection(self)

    @property
    def metadata(self):
        return sqlalchemy.BoundMetaData(self._engine)

    @property
    def session(self):
        return sqlalchemy.create_session(self._engine)

    def registerMapper(self, mapper, name):
        self._mappers.registerMapper(mapper, name)

    def getMapper(self, tablename, schema='public'):
        return self._mappers.getMapper(tablename, schema)

    def getMappers(self, *names):
        return tuple([self.getMapper(name) for name in names])

    @property
    def engine(self):
        """ only for private purposes! """
        return self._engine

    @property
    def model(self):
        """ only for private purposes! """
        return self._model

    def _createEngine(self):
        self._engine = sqlalchemy.create_engine(self.dsn, **self.kw)
        self._engine.echo = self.echo


session_cache = SynchronizedThreadCache()
connection_cache = SynchronizedThreadCache()


class SessionDataManager(object):
    """ Wraps session into transaction context of Zope """

    implements(IDataManager)

    def __init__(self, session):
        self.session = session
        self.transaction = session.create_transaction()

    def abort(self, trans):
        pass

    def commit(self, trans):
        self.session.flush()

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        self.transaction.commit()
        session_cache.set(last_session=None, last_transaction=None)
        

    def tpc_abort(self, trans):
        self.transaction.rollback()
        session_cache.set(last_session=None, last_transaction=None)

    def sortKey(self):
        return 'z3c.sqlalchemy' + str(id(self))


class ConnectionDataManager(object):
    """ Wraps connection into transaction context of Zope """

    implements(IDataManager)

    def __init__(self, connection):
        self.connection = connection
        self.transaction = connection.begin()

    def abort(self, trans):
        self.transaction.rollback()
        self.connection.close()
        self.connection = None
        connection_cache.set(last_connection=None, last_transaction=None)

    def commit(self, trans):
        self.transaction.commit()
        self.connection.close()
        self.connection = None
        connection_cache.set(last_connection=None, last_transaction=None)

    def tpc_begin(self, trans):
        pass

    def tpc_vote(self, trans):
        pass

    def tpc_finish(self, trans):
        pass

    def tpc_abort(self, trans):
        pass

    def sortKey(self):
        return 'z3c.sqlalchemy' + str(id(self))


class ZopeBaseWrapper(BaseWrapper):
    """ A wrapper to be used from within Zope. It connects
        the session with the transaction management of Zope.
    """

    @property
    def session(self):

        last_session, = session_cache.get('last_session')

        # return cached session if we are within the same transaction
        # and same thread
        if last_session is not None:
            return last_session

        # no cached session, let's create a new one
        session = sqlalchemy.create_session(self._engine)
                                          
        # register a DataManager with the current transaction
        transaction.get().join(SessionDataManager(session))

        # update thread-local cache
        session_cache.set(last_session=session)

        # return the session
        return session 

    @property
    def connection(self):

        last_connection, = connection_cache.get('last_connection')

        # return cached connection if we are within the same transaction
        # and same thread
        if last_connection is not None:
            return last_connection

        # no cached connection, let's create a new one
        connection = self.engine.connect()
                                          
        # register a DataManager with the current transaction
        transaction.get().join(ConnectionDataManager(connection))

        # update thread-local cache
        connection_cache.set(last_connection=connection)

        # return the connection
        return connection

