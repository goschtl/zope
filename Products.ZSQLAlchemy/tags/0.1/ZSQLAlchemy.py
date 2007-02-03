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


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Shared.DC.ZRDB.TM import TM
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import sqlalchemy


SUPPORTED_DATABASES = ('postgres', )


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


    security.declarePrivate('_getPool')
    def _getPool(self):
        """ create a pool and cache it(?) """
    
        pool = getattr(self, '_v_sqlalchemy_pool', None)
        if pool is None:
            pool = sqlalchemy.pool.QueuePool(self._getConnection, 
                                             max_overflow=10, 
                                             pool_size=10, 
                                             use_threadlocal=True)
            self._v_sqlalchemy_pool = pool
        return pool


    security.declarePrivate('_getEngine')
    def _getEngine(self):
        """ create an engine """
        return sqlalchemy.create_engine('%s://' % self.dbtype, pool=self._getPool())


    security.declarePublic('getSession')
    def getSession(self):
        """ return a session proxy """

        engine = self._getEngine()
        proxy = SessionProxy(engine)
        return proxy


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
