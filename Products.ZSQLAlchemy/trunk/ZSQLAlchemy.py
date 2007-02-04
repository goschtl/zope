##########################################################################
# ZSQLAlchemy
#
# (C) 2007, ZOPYX Ltd & Co. KG
# D-72070 Tuebingen, Germany
# www.zopyx.com, info@zopyx.com
#
# Written by Andreas Jung
#
# ZSQLAlchemy is published under the Zope Public License 2.1 (ZPL 2.1)
##########################################################################


import new
import threading

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Shared.DC.ZRDB.TM import TM
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import sqlalchemy


SUPPORTED_DATABASES = ('postgres', )
MAPPER_CACHE_LOCK = threading.Lock()


class SessionProxy(object, TM):
    """ A session proxy that provides basic infrastructure for applications
        working with SQLAlchemy. The proxy represents a SQLAlchemy session.
        The proxy (and therefore the SQLAlchemy sesssion) participate in
        the Zope 2 transaction handling.
    """

    security = ClassSecurityInfo()

    def __init__(self, engine):
        self._engine = engine
        self._session = sqlalchemy.create_session(bind_to=engine)
        self._register()  # register with TM

    def _finish(self):
        """ commit transaction """

        if self._session is None:
            raise RuntimeError('_session is None. This should not happen :-)')

        self._session.flush()
        self._session = None

    def _abort(self):
        """ abort transaction """
        # Nothing to do here since SQLAlchemy starts the transaction with the
        # current session only when calling its flush() method


    security.declarePublic('getEngine')
    def getEngine(self):
        """ return the engine """
        return self._engine


    security.declarePublic('getMetaData')
    def getMetaData(self):      
        """ return a MetaData instance """
        return sqlalchemy.BoundMetaData(self._engine)


    security.declarePublic('getSession')
    def getSession(self):      
        """ return the session itself"""
        return self._session

InitializeClass(SessionProxy)



class ZSQLAlchemy(SimpleItem, PropertyManager):

    meta_type = 'ZSQLAlchemy'

    hostname = ''
    port     = 0
    username = ''
    password = ''
    database = ''
    dbtype   = ''

    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options 

    _properties=({'id':'dbtype',  'type':'selection', 'mode':'wr', 'select_variable':'dbTypes'},
                 {'id':'hostname', 'type':'string', 'mode':'wr'},
                 {'id':'port', 'type':'int', 'mode':'wr'},
                 {'id':'username', 'type':'string', 'mode':'wr'},
                 {'id':'password', 'type':'string', 'mode':'wr'},
                 {'id':'database', 'type':'string', 'mode':'wr'},
                 )

    security = ClassSecurityInfo()


    security.declarePrivate('dbTypes')
    def dbTypes(self):
        return SUPPORTED_DATABASES


    security.declarePrivate('_getConnection')
    def _getConnection(self):
        """ connection factory """

        if self.dbtype == 'postgres':

            import psycopg2 as psycopg

            psycopg = sqlalchemy.pool.manage(psycopg)
            db = psycopg.connect(database=self.database, 
                                 user=self.username,
                                 password=self.password,        
                                 port=self.port,
                                 host=self.hostname)
            return db

        else:
            raise ValueError('Unsupported dbtype (%s)' % self.dbtype)


    @property
    def enginePool(self):
        """ create a pool and cache it(?) """
    
        if not hasattr(self, '_v_sqlalchemy_pool'):
            pool = sqlalchemy.pool.QueuePool(self._getConnection, 
                                             max_overflow=10, 
                                             pool_size=10, 
                                             use_threadlocal=True)
            self._v_sqlalchemy_pool = pool

        return self._v_sqlalchemy_pool 


    @property
    def engine(self):
        """ create an engine """
        return sqlalchemy.create_engine('%s://' % self.dbtype, pool=self.enginePool)


    security.declarePublic('getSession')
    def getSession(self):
        """ return a session proxy """
        return SessionProxy(self.engine)

    @property
    def mapperCache(self):
        """ we cache the (mapperCls, tableCls) pair for 
            performance reasons.
        """
        if not hasattr(self, '_v_mapper_cache'):
           self._v_mapper_cache = {}
        return self._v_mapper_cache


    security.declarePublic('createMapper')
    def createMapper(self, tablename, properties={}):
        """ create a mapper class and table for a given 'tablename' """

        def myStr(cls):               
            """ textual representation for a mapper class """
            return '%s' % (cls.__name__,)

        # check for a cached entry
        cls, table = self.mapperCache.get(tablename, (None, None))

        if cls is None and table is None:
            
            # create a new mapper and table classes

            metadata = sqlalchemy.BoundMetaData(self.engine)
            table = sqlalchemy.Table(tablename, metadata, autoload=True)                                                                                                        
            newCls = new.classobj(tablename, (object,), {})
            newCls.__str__ = classmethod(myStr)
            newCls.__repr__ = classmethod(myStr)
            sqlalchemy.mapper(newCls, table, properties=properties)

            MAPPER_CACHE_LOCK.acquire()
            self.mapperCache[tablename] = (newCls, table)
            MAPPER_CACHE_LOCK.release()
            return newCls, table   

        return cls, table

InitializeClass(ZSQLAlchemy)


manage_addZSQLAlchemyForm = PageTemplateFile( "pt/add.pt", globals(), __name__ = 'manage_addZSQLAlchemyForm')

def manage_addZSQLAlchemy(self, id, REQUEST=None):
    """ """

    zs = ZSQLAlchemy(id)
    self._setObject(id, zs)

    if REQUEST:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')
    else:
        return zs
